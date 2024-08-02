import pandas as pd
import numpy as np
from django.db import connection
import logging

log = logging.getLogger(__name__)


def player_stats(player_id, start_at, params):
    params["player_id"] = player_id
    params["start_at"] = start_at
    query = """
            select
               round(avg(SPW), 2) as SPW,
               round(avg(RPW), 2) as RPW,
               round(avg(RPW)/(1-avg(SPW)),2) as DR,
               count(*) as matches
            from (
            select
               (firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW,
               (opponen_service_points - opponen_firstwon - opponen_secondwon) / nullif(opponen_service_points::numeric, 0) as RPW,
               service_points - firstwon - secondwon as service_points_lost,
               opponen_service_points - opponen_firstwon - opponen_secondwon as return_points_won
            from (
            select
            distinct on (date)
               t.date,
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
            from %(matches_table)s t 
            where (winner_id=%(player_id)s or loser_id=%(player_id)s)
               and surface ilike '%%%(surface)s%%'
               and round_name not ilike 'qualification%%'
               --and t.date >= date(%(start_at)s)
               ) a order by date desc limit %(limit)s
            ) s
        """
    df = pd.read_sql(query, connection, params=params)
    spw = df.iloc[0]["spw"]
    rpw = df.iloc[0]["rpw"]
    matches = df.iloc[0]["matches"]

    return [spw, rpw, matches]


def opponent_hard_elo(opponent_id, params):
    params["player_id"] = opponent_id
    query = """
        select elo as opponent_hard from %(hard_elo)s where player_id = %(player_id)s
        order by date desc limit 1
    """

    df = pd.read_sql(query, connection, params=params)

    if df.empty:
        return pd.DataFrame({"opponent_hard": [1500]})

    return df

def opponent_clay_elo(opponent_id, params):
    params["player_id"] = opponent_id
    query = """
        select elo as opponent_clay from %(clay_elo)s where player_id = %(player_id)s
        order by date desc limit 1
    """

    df = pd.read_sql(query, connection, params=params)

    if df.empty:
        return pd.DataFrame({"opponent_clay": [1500]})

    return df


def match_stats(player_id, start_at, params):
    params["player_id"] = player_id
    params["start_at"] = start_at
    query = """
        select
            date,
            surface,
            round_name,
            tourney_name,
            opponent_name,
            SPW,
            RPW,
            service_points_lost,
            return_points_won,
            round(RPW/(1-nullif(SPW, 0)),2) as DR,
            opponent_id
        from (
            select
                date,
                surface,
                round_name,
                tourney_name,
                opponent_name,
                opponent_id,
                round((firstwon + secondwon) / nullif(service_points::numeric, 0), 2) as SPW,
                round((opponen_service_points - opponen_firstwon - opponen_secondwon) / nullif(opponen_service_points::numeric, 0), 2) as RPW,
                service_points - firstwon - secondwon as service_points_lost,
                opponen_service_points - opponen_firstwon - opponen_secondwon as return_points_won
            from (
            select
            distinct on (date)
               t.date,
                t.surface,
                t.round_name,
                t.tourney_name,
                case when winner_id = %(player_id)s
               then loser_name
               else winner_name end as opponent_name,
               case when winner_id = %(player_id)s
               then loser_id
               else winner_id end as opponent_id,
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
            from %(matches_table)s t
            where (winner_id=%(player_id)s or loser_id=%(player_id)s)
               and surface ilike '%%%(surface)s%%'
               and round_name not ilike 'qualification%%'
               --and t.date >= date(%(start_at)s)
               ) a order by date desc limit %(limit)s
            ) s
        """
    df = pd.read_sql(query, connection, params=params)
    columns = [
        "date",
        "surface",
        "round_name",
        "tourney_name",
        "spw",
        "rpw",
        "opponent_name",
        "dr",
        "opponent_id",
    ]
    df = df[columns]
    # replace Nan with ''
    df = df.fillna("")

    df[["opponent_hard"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(opponent_hard_elo, otypes=["O"])(
                df["opponent_id"], params
            )
        ),
        index=df.index,
    )
    df[["opponent_clay"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(opponent_clay_elo, otypes=["O"])(
                df["opponent_id"], params
            )
        ),
        index=df.index,
    )

    return df
