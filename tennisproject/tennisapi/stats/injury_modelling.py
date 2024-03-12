import pandas as pd
from django.db import connection
import warnings
from psycopg2.extensions import AsIs
warnings.filterwarnings("ignore")


def injury_score(params):
    query = \
        """
            select 
                s.*,
                case when (
                    loser_id = %(player_id)s 
                    and w_svgms is null
                    ) then 1 else 0 end as walkover,
                round((1 + pow(1.02, EXTRACT(DAY from now() - date)))::numeric, 2) as injury_score
            from (
                select
                a.date,
                a.tourney_name,
                w_svgms,
                l_svgms,
                winner_code,
                loser_id
                from %(matches_table)s a
                where 
                (winner_id = %(player_id)s
                or loser_id = %(player_id)s)
                and a.date < %(date)s
                order by a.date desc
            ) s
        """

    df = pd.read_sql(query, connection, params=params)

    if df.empty:
        walkover = None
        score = None
    else:
        walkover = df.iloc[0]['walkover']
        score = df.iloc[0]['injury_score']

    return [walkover, score]


def injury_modelling(date, player_id, tour_table, matches_table):

    params = {
        'tour_table': AsIs(tour_table),
        'matches_table': AsIs(matches_table),
        'player_id': player_id,
        'date': date,
    }

    score = injury_score(params)

    return score
