import warnings
import numpy as np
import pandas as pd
from django.db import connection
import os
from datetime import datetime, timedelta
from django.utils import timezone
import joblib
import logging
import sys
from psycopg2.extensions import AsIs
from footballapi.models import Teams, PremierLeague, Championship
from footballapi.ml.train_model import train_ml_model
import logging
from tabulate import tabulate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

warnings.filterwarnings("ignore")


def probability_of_winning(x):
    l = (x) / 400
    prob2win = 1 / (1 + 10 ** (l))
    return 1 - prob2win


def get_data(params):
    query = \
        """
            select 
                home_team_id,
                away_team_id,
                b.start_at,
                b.id as match_id,
                home_odds,
                draw_odds,
                away_odds,
                h.name as home_name,
                aw.name as away_name,
                winner_code,
                (select elo from %(elo_table)s elo where elo.team_id=home_team_id and elo.date < date(b.start_at) order by games desc limit 1) as home_elo,
                (select elo from %(elo_table)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as away_elo
            from %(match_table)s b
            left join footballapi_teams h on h.id = b.home_team_id
            left join footballapi_teams aw on aw.id = b.away_team_id
            where  b.start_at between %(start_at)s and %(end_at)s
            order by start_at
        """

    df = pd.read_sql(query, connection, params=params)

    return df


def label_round(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data


def predict(level):
    teams_qs = Teams.objects.all()
    if level == 'premier':
        match_qs = PremierLeague.objects.all()
        match_table = 'footballapi_premierleague'
        elo_table = 'footballapi_premierelo'
    else:
        match_qs = Championship.objects.all()
        match_table = 'footballapi_championship'
        elo_table = 'footballapi_championshipelo'
    params = {
        'match_table': AsIs(match_table),
        'elo_table': AsIs(elo_table),
        'start_at': '2024-02-03 00:00:00',
        'end_at': '2024-02-03 22:00:00',
    }
    data = get_data(params)
    l = len(data.index)
    if l == 0:
        print("No data")
        return

    columns = [
        'start_at',
        'home_name',
        'away_name',
        'home_odds',
        'draw_odds',
        'away_odds',
        'home_elo',
        'away_elo',
        'elo_prob',
    ]

    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)

    data['elo_prob'] = data['home_elo'] - data['away_elo']
    data['elo_prob'] = data['elo_prob'].apply(probability_of_winning).round(2)
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}")

    data = data.replace(np.nan, None, regex=True)
    for index, row in data.iterrows():
        train_ml_model(row, level, params)
        """try:
            train_ml_model(row, level, params)
        except Exception as e:
            logging.error(e)
            pass"""

