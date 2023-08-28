import pandas as pd
from django.db import connection


def player_stats(player_id):
    query = "select " \
            "round(avg(SPW), 2) as SPW, " \
	        "round(avg(RPW), 2) as RPW, " \
            "round(avg(RPW)/(1-avg(SPW)),2) as DR " \
        "from ( " \
        "select " \
            "(firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW, " \
            "(opponen_service_points - opponen_firstwon - opponen_secondwon) / nullif(opponen_service_points::numeric, 0) as RPW, " \
            "service_points - firstwon - secondwon as service_points_lost, " \
            "opponen_service_points - opponen_firstwon - opponen_secondwon as return_points_won " \
        "from ( " \
        "select " \
            "t.date, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then w_svpt " \
            "else l_svpt end as service_points, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then w_firstwon " \
            "else l_firstwon end as firstwon, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then w_secondwon " \
            "else l_secondwon end as secondwon, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then l_svpt " \
            "else w_svpt end as opponen_service_points, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then l_firstwon " \
            "else w_firstwon end as opponen_firstwon, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then l_secondwon " \
            "else w_secondwon end as opponen_secondwon " \
        "from tennisapi_atpmatches t inner join tennisapi_atptour e on t.tour_id=e.id " \
        "where (winner_id='"+str(player_id)+"' or loser_id='"+str(player_id)+"') " \
            "and surface ilike '%hard%' " \
        ") a order by date desc limit 20 " \
        ") s ; "
    df = pd.read_sql(query, connection)
    df = df.iloc[0]['dr']

    return df


def player_stats_wta(player_id):
    query = "select " \
            "round(avg(SPW), 2) as SPW, " \
	        "round(avg(RPW), 2) as RPW, " \
            "round(avg(RPW)/(1-avg(SPW)),2) as DR " \
        "from ( " \
        "select " \
            "(firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW, " \
            "(opponen_service_points - opponen_firstwon - opponen_secondwon) / nullif(opponen_service_points::numeric, 0) as RPW, " \
            "service_points - firstwon - secondwon as service_points_lost, " \
            "opponen_service_points - opponen_firstwon - opponen_secondwon as return_points_won " \
        "from ( " \
        "select " \
            "t.date, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then w_svpt " \
            "else l_svpt end as service_points, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then w_firstwon " \
            "else l_firstwon end as firstwon, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then w_secondwon " \
            "else l_secondwon end as secondwon, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then l_svpt " \
            "else w_svpt end as opponen_service_points, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then l_firstwon " \
            "else w_firstwon end as opponen_firstwon, " \
            "case when winner_id = '"+str(player_id)+"' " \
            "then l_secondwon " \
            "else w_secondwon end as opponen_secondwon " \
        "from tennisapi_wtamatches t inner join tennisapi_wtatour e on t.tour_id=e.id " \
        "where (winner_id='"+str(player_id)+"' or loser_id='"+str(player_id)+"') " \
            "and surface ilike '%hard%' " \
        ") a order by date desc limit 20 " \
        ") s ; "
    df = pd.read_sql(query, connection)
    df = df.iloc[0]['dr']

    return df
