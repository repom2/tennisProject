import pandas as pd
from django.db import connection
import warnings
from psycopg2.extensions import AsIs
warnings.filterwarnings("ignore")


def head_to_head_win_percentage(params):
    query = \
        """
        select 
            round(sum(player_1_won)::numeric / count(*)::numeric, 2) as player_1_won_percentage,
            count(*) as count 
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

    score = df.iloc[0]['player_1_won_percentage']
    count = df.iloc[0]['count']

    return [score, count]


def head2head(player1, player2, tour_table, matches_table):
    params = {
        'tour_table': AsIs(tour_table),
        'matches_table': AsIs(matches_table),
        'player1': player1,
        'player2': player2,
    }

    score = head_to_head_win_percentage(params)

    return score
