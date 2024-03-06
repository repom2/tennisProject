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
                    away_id = %(player_id)s 
                    and w_svgms is null
                    ) then 1 else 0 end as walkover,
                round((1 + pow(1.02, EXTRACT(DAY from now() - date)))::numeric, 2) as injury_score
            from (
                select
                a.start_at as date,
                t.slug,
                w_svgms,
                l_svgms,
                winner_code,
                away_id
                from %(match_table)s a inner join %(tour_table)s t on a.tour_id=t.id 
                where 
                (home_id = %(player_id)s
                or away_id = %(player_id)s)
                and a.start_at < %(date)s
                order by a.start_at desc
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


def injury_modelling(date, player_id, tour_table, match_table):

    params = {
        'tour_table': AsIs(tour_table),
        'match_table': AsIs(match_table),
        'player_id': player_id,
        'date': date,
    }

    score = injury_score(params)

    return score
