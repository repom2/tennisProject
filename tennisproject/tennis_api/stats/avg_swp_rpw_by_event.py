import pandas as pd
from django.db import connection


def event_stats(params):
    query = \
        """
            select 
                *, 
                (SPW + loser_SPW) / 2 as avg_SPW,
                (RPW + loser_RPW) / 2 as avg_RPW,
                (DR + loser_DR) / 2 as avg_DR
            from (select
                round(avg(SPW), 2) as SPW,
                round(avg(loser_SPW), 2) as loser_SPW,
                round(avg(RPW), 2) as RPW,
                round(avg(loser_RPW), 2) as loser_RPW,
                round(avg(RPW)/ avg(loser_RPW),2) as DR,
                round(avg(loser_RPW)/(avg(RPW)),2) as loser_DR
            from (
            select
                (firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW,
                (opponent_firstwon + opponent_secondwon) / nullif(opponent_service_points::numeric, 0) as loser_SPW,
                (opponent_service_points - opponent_firstwon - opponent_secondwon) / nullif(opponent_service_points::numeric, 0) as RPW,
                (service_points - firstwon - secondwon) / nullif(service_points::numeric, 0) as loser_RPW,
                service_points - firstwon - secondwon as service_points_lost,
                opponent_service_points - opponent_firstwon - opponent_secondwon as return_points_won
            from (
            select
                t.start_at as date,
                w_svpt as service_points, \
                w_firstwon as firstwon,
                w_secondwon as secondwon,
                l_svpt as opponent_service_points,
                l_firstwon as opponent_firstwon,
                l_secondwon as opponent_secondwon
            from  %(match_table)s t inner join %(tour_table)s e on t.tour_id=e.id
            where
                surface ilike '%%%(surface)s%%' and (slug ilike '%%%(event)s%%' ) and t.start_at > %(date)s
            ) a 
            ) s ) aa; 
    """

    df = pd.read_sql(query, connection, params=params)
    avg_spw = df.iloc[0]['avg_spw']
    avg_rpw = df.iloc[0]['avg_rpw']

    return avg_spw, avg_rpw
