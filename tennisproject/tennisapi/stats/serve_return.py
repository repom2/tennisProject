import pandas as pd
from django.db import connection
from tennisapi.models import AtpMatches
from tennisapi.stats.prob_by_serve.winning_match import matchProb


def player_stats():
    query = (
        "select *, (SPW + loser_SPW) / 2 as avg_SWP, "
        "(RPW + loser_RPW) / 2 as avg_RPW, "
        "(DR + loser_DR) / 2 as avg_DR "
        "from (select "
        "round(avg(SPW), 2) as SPW, "
        "round(avg(loser_SPW), 2) as loser_SPW, "
        "round(avg(RPW), 2) as RPW, "
        "round(avg(loser_RPW), 2) as loser_RPW, "
        "round(avg(RPW)/ avg(loser_RPW),2) as DR, "
        "round(avg(loser_RPW)/(avg(RPW)),2) as loser_DR "
        "from ( "
        "select "
        "(firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW, "
        "(opponent_firstwon + opponent_secondwon) / nullif(opponent_service_points::numeric, 0) as loser_SPW, "
        "(opponent_service_points - opponent_firstwon - opponent_secondwon) / nullif(opponent_service_points::numeric, 0) as RPW, "
        "(service_points - firstwon - secondwon) / nullif(service_points::numeric, 0) as loser_RPW, "
        "service_points - firstwon - secondwon as service_points_lost, "
        "opponent_service_points - opponent_firstwon - opponent_secondwon as return_points_won "
        "from ( "
        "select "
        "t.date, "
        "w_svpt as service_points,"
        "w_firstwon as firstwon, "
        "w_secondwon as secondwon, "
        "l_svpt as opponent_service_points, "
        "l_firstwon as opponent_firstwon, "
        "l_secondwon as opponent_secondwon "
        "from tennisapi_atpmatches t "
        "where "
        "surface ilike '%%%(surface)s%%' and (name ilike '%us%pen%' ) "
        ") a  "
        ") s ) aa; "
    )

    df = pd.read_sql(query, connection)
    avg_swp = df.iloc[0]["avg_swp"]

    print(df)

    return avg_swp


def player_stats_points():
    query = (
        "select *, (SPW + loser_SPW) / 2 as avg_SWP, "
        "(RPW + loser_RPW) / 2 as avg_RPW, "
        "(RPW/ loser_RPW + loser_RPW/RPW) / 2 as avg_DR "
        "from ( "
        "select "
        "sum(firstwon + secondwon) / sum(service_points::numeric) as SPW, "
        "sum(opponent_firstwon + opponent_secondwon) / sum(opponent_service_points::numeric) as loser_SPW, "
        "sum(opponent_service_points - opponent_firstwon - opponent_secondwon) / sum(opponent_service_points::numeric) as RPW, "
        "sum(service_points - firstwon - secondwon) / sum(service_points::numeric) as loser_RPW, "
        "sum(service_points - firstwon - secondwon) as service_points_lost, "
        "sum(opponent_service_points - opponent_firstwon - opponent_secondwon) as return_points_won "
        "from ( "
        "select "
        "t.date, "
        "w_svpt as service_points,"
        "w_firstwon as firstwon, "
        "w_secondwon as secondwon, "
        "l_svpt as opponent_service_points, "
        "l_firstwon as opponent_firstwon, "
        "l_secondwon as opponent_secondwon "
        "from tennisapi_atpmatches t "
        "where "
        "surface ilike '%hard%' "
        ") a ) s "
    )

    df = pd.read_sql(query, connection)
    # df = df.iloc[0]['dr']

    print(df)

    return df.iloc[0]["avg_swp"], df.iloc[0]["avg_rpw"]


def serve_points():
    open_spw = player_stats()
    all_spw, all_rpw = player_stats_points()
    player = 0.5
    player_rpw = 0.2
    print(open_spw)
    # James - Stein Estimator
    result = open_spw + (player - all_spw) - (player_rpw - all_rpw)
    print(result)

    ## s, t: p(server wins a service point), p(server wins return point)
    ## gv, gw: current score within the game. e.g. 30-15 is 2, 1
    ## sv, sw: current score within the set. e.g. 5, 4
    ## mv, mw: current score within the match (number of sets for each player)
    ## v's are serving player; w's are returning player
    ## sets: "best of", so default is best of 3
    win = matchProb(0.6221, 1 - 0.6199, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=5)

    print(win)
