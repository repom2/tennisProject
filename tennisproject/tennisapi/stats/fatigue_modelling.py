import pandas as pd
from django.db import connection
import warnings
from psycopg2.extensions import AsIs
warnings.filterwarnings("ignore")


def fatigue_score(params):
    # alternative 1 / 1 + 0.75*days
    query = \
        """
            select sum(court_time * pow(0.75 ,days)) / 3600 as fatigue_score from (
            select 
            court_time, EXTRACT(DAY from now() - a.date) as days, a.date
            from %(matches_table)s a inner join %(tour_table)s t on a.tour_id=t.id 
            where 
            (
            winner_id = %(player_id)s
            or loser_id = %(player_id)s
            )
            and t.date > '2015-1-1'
            order by a.date desc limit 14
                ) s;
        """

    df = pd.read_sql(query, connection, params=params)

    print(df)

    return df

def fatigue_modelling():

    #f1643cdd078cb77d173c609bd72a32 kenin
    #a8225539ce9e7f4aab1b2d0f55fa01d4

    params = {
        'tour_table': AsIs('tennisapi_wtatour'),
        'matches_table': AsIs('tennisapi_wtamatches'),
        'player_id': 'a8225539ce9e7f4aab1b2d0f55fa01d4',
    }

    fatigue_score(params)