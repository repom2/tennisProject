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
from icehockeyapi.models import Teams, Liiga, BetIceHockey
from icehockeyapi.ml.train_model import train_ml_model
import logging
from tabulate import tabulate
from django.contrib.contenttypes.models import ContentType
import unicodedata
from django.db.models import Avg
from icehockeyapi.stats.estimated_goals import estimated_goals
from icehockeyapi.stats.poisson import calculate_poisson

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
                (select avg(home_score) from %(match_table)s l where l.home_team_id=b.home_team_id and l.start_at < date(b.start_at)) as home_goals,
				(select avg(away_score) from %(match_table)s l where l.home_team_id=b.home_team_id and l.start_at < date(b.start_at)) as home_conceded,
				(select avg(away_score) from %(match_table)s l where l.away_team_id=b.away_team_id and l.start_at < date(b.start_at)) as away_goals,
				(select avg(home_score) from %(match_table)s l where l.away_team_id=b.away_team_id and l.start_at < date(b.start_at)) as away_conceded,
                (select elo from %(elo_table)s elo where elo.team_id=home_team_id and elo.date < date(b.start_at) order by games desc limit 1) as home_elo,
                (select elo from %(elo_table)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as away_elo,
                (select elo from %(elo_home)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_home,
                (select elo from %(elo_away)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_away
            from %(match_table)s b
            left join icehockeyapi_teams h on h.id = b.home_team_id
            left join icehockeyapi_teams aw on aw.id = b.away_team_id
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
    bet_qs = BetIceHockey.objects.all()
    if level == 'liiga':
        match_qs = Liiga.objects.all()
        league_avg_home_goals = Liiga.objects.aggregate(
            home_goals=Avg('home_score'))
        league_avg_away_goals = Liiga.objects.aggregate(
            away_goals=Avg('away_score'))
        match_table = 'icehockeyapi_liiga'
        elo_table = 'icehockeyapi_liigaelo'
        elo_home = 'icehockeyapi_liigaelohome'
        elo_away = 'icehockeyapi_liigaeloaway'
    else:
        return
    logging.info(f'Average home goals: {league_avg_home_goals}')
    logging.info(f'Average away goals: {league_avg_away_goals}')

    now = timezone.now().date()
    end_at = now + timedelta(days=1)
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
    data[['home_est_goals', 'away_est_goals']] = pd.DataFrame(
        np.row_stack(
            np.vectorize(estimated_goals, otypes=['O'])(
                league_avg_home_goals['home_goals'],
                league_avg_away_goals['away_goals'],
                data['home_goals'],
                data['home_conceded'],
                data['away_goals'],
                data['away_conceded']
            )
        ), index=data.index)

    data[['home_poisson', 'draw_poisson', 'away_poisson']] = pd.DataFrame(
        np.row_stack(
            np.vectorize(calculate_poisson, otypes=['O'])(
                data['home_est_goals'],
                data['away_est_goals'],
            )
        ), index=data.index)
    logging.info(
        f"DataFrame:\n{tabulate(data[['home_name', 'away_name', 'home_est_goals', 'away_est_goals', 'home_poisson', 'draw_poisson', 'away_poisson', 'home_goals', 'home_conceded', 'away_goals', 'away_conceded', ]], headers='keys', tablefmt='psql', showindex=True)}")


    data = data.replace(np.nan, None, regex=True)
    for index, row in data.iterrows():
        data = train_ml_model(row, level, params, league_avg_home_goals, league_avg_away_goals)
        if data is None:
            continue
        match = match_qs.get(id=row.match_id)
        content_type = ContentType.objects.get_for_model(match)
        object_id = match.id
        home_name = unicodedata.normalize(
            'NFKD', row.home_name).encode('ASCII', 'ignore').decode('ASCII')
        away_name = unicodedata.normalize(
            'NFKD', row.away_name).encode('ASCII', 'ignore').decode('ASCII')
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
                # "preview": preview,
                # "reasoning": reasoning,
                "home_prob": data['prob_home'],
                "draw_prob": data['prob_draw'],
                "away_prob": data['prob_away'],
                "home_yield": data['home_yield'],
                "draw_yield": data['draw_yield'],
                "away_yield": data['away_yield'],
                "home_est_goals": row['home_est_goals'],
                "away_est_goals": row['away_est_goals'],
                "home_poisson": row['home_poisson'],
                "draw_poisson": row['draw_poisson'],
                "away_poisson": row['away_poisson'],
                "level": level,
            }
        )

