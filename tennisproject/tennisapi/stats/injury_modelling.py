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
                    loser_id = 'bdfffb65d7c7683a9c85c8b1e1fe39c2' 
                    and w_svgms is null
                    ) then 1 else 0 end as walkover,
                1 + pow(1.02, EXTRACT(DAY from now() - date)) as injury_score
                
            from (
                select
                a.date,
                t.name,
                d.last_name, 
                e.last_name, 
                w_svgms,
                l_svgms,
                winner_code,
                loser_id
                from %(matches_table)s a inner join %(tour_table) t on a.tour_id=t.id 
                where 
                (winner_id = %(player_id)s
                or loser_id = %(player_id)s)
                and a.date < %(date)s
                order by a.date desc
            ) s;
        """

    df = pd.read_sql(query, connection, params=params)

    print(df)

    return df


def fatigue_modelling(date, player_id):
    params = {
        'tour_table': AsIs('tennisapi_wtatour'),
        'matches_table': AsIs('tennisapi_wtamatches'),
        'player_id': player_id,
        'date': date,
    }

    fatigue_score(params)
