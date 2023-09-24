import pandas as pd
from django.db import connection
import warnings
from psycopg2.extensions import AsIs
warnings.filterwarnings("ignore")


def head_to_head_win_percentage(params):
    query = \
        """
        select sum(player_1_won)::numeric / count(*)::numeric as player_1_won_percentage 
        from (
            select 
                case when winner_id = %(player1)s then  1 else 0 end player_1_won,
                case when winner_id = %(player2)s then  1 else 0 end player_2_won
            
            from %(matches_table)s a inner join %(tour_table)s t on a.tour_id=t.id 
            where 
            (winner_id = %(player1)s and loser_id = %(player2)s)
            or
            (winner_id = %(player2)s and loser_id = %(player1)s)
        ) s
        """

    df = pd.read_sql(query, connection, params=params)

    print(df)

    return df


def head2head():
    player1 = 'ef4d3319eb3a6a2e9fdc8841752450b1'
    player2 = 'fa6be5d12f49f59ebc105e3fad1e171d'
    params = {
        'tour_table': AsIs('tennisapi_wtatour'),
        'matches_table': AsIs('tennisapi_wtamatches'),
        'player1': player1,
        'player2': player2,
    }

    head_to_head_win_percentage(params)


