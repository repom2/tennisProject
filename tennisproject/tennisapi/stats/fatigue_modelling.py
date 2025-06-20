import warnings

import pandas as pd
from django.db import connection
from psycopg2.extensions import AsIs

warnings.filterwarnings("ignore")


def fatigue_score(params):
    # alternative 1 / 1 + 0.75*days
    query = """
            select round((sum(court_time * pow(0.75 ,days)) / 3600)::numeric, 2) as fatigue_score from (
            select 
            court_time, EXTRACT(DAY from now() - a.date) as days, a.date
            from %(matches_table)s a 
            where 
            (
            winner_id = %(player_id)s
            or loser_id = %(player_id)s
            )
            and a.date between (date(%(start_at)s) - interval '1 year') and %(start_at)s
            order by a.date desc limit 14
                ) s;
        """
    try:
        df = pd.read_sql(query, connection, params=params)
        score = df.iloc[0]["fatigue_score"]
    except:
        score = None

    return score


def fatigue_modelling(player_id, tour_table, matches_table, start_at):

    params = {
        "tour_table": AsIs(tour_table),
        "matches_table": AsIs(matches_table),
        "player_id": player_id,
        "start_at": start_at,
    }

    score = fatigue_score(params)
    return score
