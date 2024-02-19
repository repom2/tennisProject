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
from footballapi.models import Teams, PremierLeague, Championship, LaLiga, SerieA, Bundesliga, Ligue1, BetFootball
from django.contrib.contenttypes.models import ContentType
from footballapi.ml.train_model import train_ml_model
import logging
from tabulate import tabulate
import unicodedata

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
                (select elo from %(elo_table)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as away_elo,
                (select elo from %(elo_home)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_home,
                (select elo from %(elo_away)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_away
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
    bet_qs = BetFootball.objects.all()
    if level == 'premier':
        match_qs = PremierLeague.objects.all()
        match_table = 'footballapi_premierleague'
        elo_table = 'footballapi_premierelo'
        elo_home = 'footballapi_premierelohome'
        elo_away = 'footballapi_premiereloaway'
    elif level == 'laliga':
        match_qs = LaLiga.objects.all()
        match_table = 'footballapi_laliga'
        elo_table = 'footballapi_laligaelo'
        elo_home = 'footballapi_laligaelohome'
        elo_away = 'footballapi_laligaeloaway'
    elif level == 'bundesliga':
        match_qs = Bundesliga.objects.all()
        match_table = 'footballapi_bundesliga'
        elo_table = 'footballapi_bundesligaelo'
        elo_home = 'footballapi_bundesligaelohome'
        elo_away = 'footballapi_bundesligaeloaway'
    elif level == 'seriea':
        match_qs = SerieA.objects.all()
        match_table = 'footballapi_seriea'
        elo_table = 'footballapi_serieaelo'
        elo_home = 'footballapi_serieaelohome'
        elo_away = 'footballapi_serieaeloaway'
    elif level == 'ligue1':
        match_qs = Ligue1.objects.all()
        match_table = 'footballapi_ligue1'
        elo_table = 'footballapi_ligue1elo'
        elo_home = 'footballapi_ligue1elohome'
        elo_away = 'footballapi_ligue1eloaway'
    elif level == 'facup':
        match_table = 'footballapi_facup'
        elo_table = 'footballapi_championshipelo'
        elo_home = 'footballapi_championshipelohome'
        elo_away = 'footballapi_championshipeloaway'
        elo_table = 'footballapi_premierelo'
        elo_home = 'footballapi_premierelohome'
        elo_away = 'footballapi_premiereloaway'
    else:
        match_qs = Championship.objects.all()
        match_table = 'footballapi_championship'
        elo_table = 'footballapi_championshipelo'
        elo_home = 'footballapi_championshipelohome'
        elo_away = 'footballapi_championshipeloaway'

    now = timezone.now().date()
    end_at = now + timedelta(days=1)
    logging.info(f"Predicting matches for {level} between {now} and {end_at}")

    params = {
        'match_table': AsIs(match_table),
        'elo_table': AsIs(elo_table),
        'elo_home': AsIs(elo_home),
        'elo_away': AsIs(elo_away),
        'start_at': now,
        'end_at': end_at,
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
        'elo_prob_home',
    ]

    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)

    data['elo_prob'] = data['home_elo'] - data['away_elo']
    data['elo_prob'] = data['elo_prob'].apply(probability_of_winning).round(2)
    data['elo_prob_home'] = data['elo_home'] - data['elo_away']
    data['elo_prob_home'] = data['elo_prob_home'].apply(probability_of_winning).round(2)
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}")
    #exit()
    data = data.replace(np.nan, None, regex=True)
    for index, row in data.iterrows():
        data = train_ml_model(row, level, params)
        match = match_qs.get(id=row.match_id)
        content_type = ContentType.objects.get_for_model(match)
        object_id = match.id
        home_name = unicodedata.normalize('NFKD', row.home_name).encode('ASCII', 'ignore').decode('ASCII')
        away_name = unicodedata.normalize('NFKD', row.away_name).encode('ASCII', 'ignore').decode('ASCII')
        bet_qs.update_or_create(
            content_type=content_type,
            object_id=object_id,
            home=teams_qs.filter(id=row.home_team_id)[0],
            away=teams_qs.filter(id=row.away_team_id)[0],
            defaults={
                "start_at": row.start_at,
                "home_name": home_name,
                "away_name": away_name,
                "home_odds": row['home_odds'],
                "draw_odds": row['draw_odds'],
                "away_odds": row['away_odds'],
                "elo_prob": row['elo_prob'],
                "elo_prob_home": row['elo_prob_home'],
                "home_elo": row['home_elo'],
                "away_elo": row['away_elo'],
                "elo_home": row['elo_home'],
                "elo_away": row['elo_away'],
                #"preview": preview,
                #"reasoning": reasoning,
                "home_prob": data['prob_home'],
                "draw_prob": data['prob_draw'],
                "away_prob": data['prob_away'],
                "home_yield": data['home_yield'],
                "draw_yield": data['draw_yield'],
                "away_yield": data['away_yield'],
                "level": level,
            }
        )

