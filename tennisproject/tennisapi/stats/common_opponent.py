import warnings

import pandas as pd
from django.db import connection

warnings.filterwarnings("ignore")


def player_opponents(params):
    query = """
            select
               date,
               opponent,
               (firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW,
               (opponen_service_points - opponen_firstwon - opponen_secondwon) / nullif(opponen_service_points::numeric, 0) as RPW,
               service_points - firstwon - secondwon as service_points_lost,
               opponen_service_points - opponen_firstwon - opponen_secondwon as return_points_won
            from (
            select 
                a.date,
                case when winner_id = %(player_id)s then  loser_id else winner_id end as opponent,
                case when winner_id = %(player_id)s
                then w_svpt
                else l_svpt end as service_points,
                case when winner_id = %(player_id)s
                then w_firstwon
                else l_firstwon end as firstwon,
                case when winner_id = %(player_id)s
                then w_secondwon
                else l_secondwon end as secondwon,
                case when winner_id = %(player_id)s
                then l_svpt
                else w_svpt end as opponen_service_points,
                case when winner_id = %(player_id)s
                then l_firstwon
                else w_firstwon end as opponen_firstwon,
                case when winner_id = %(player_id)s
                then l_secondwon
                else w_secondwon end as opponen_secondwon
            from %(matches_table)s a 
            where surface ilike '%%%(query_surface)s%%' and 
            (winner_id = %(player_id)s or loser_id = %(player_id)s)
            and a.date between (date(%(start_at)s) - interval '2 year') and %(start_at)s
            ) s order by date desc
        """

    df = pd.read_sql(query, connection, params=params)

    return df


def common_opponent(params, player1, player2, event_spw, start_at):

    params["start_at"] = start_at
    params["player_id"] = player1
    player1 = player_opponents(params)
    params["player_id"] = player2
    player2 = player_opponents(params)

    common = list(set(player2.opponent))
    player1 = player1[player1["opponent"].isin(common)]
    common = list(set(player1.opponent))
    player2 = player2[player2["opponent"].isin(common)]

    count = len(player1)

    player1_spw = player1["spw"].mean()
    player1_rpw = player1["rpw"].mean()

    player2_spw = player2["spw"].mean()
    player2_rpw = player2["rpw"].mean()
    tour_spw, tour_rpw = 0.565, 0.435

    player1 = event_spw + (player1_spw - tour_spw) - (player2_rpw - tour_rpw)
    player2 = event_spw + (player2_spw - tour_spw) - (player1_rpw - tour_rpw)

    return [player1, player2, count]
