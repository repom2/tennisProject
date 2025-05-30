import pandas as pd
from django.db import connection
import logging

log = logging.getLogger(__name__)


def player_stats(player_id, start_at, params):
    params['player_id'] = player_id
    params['start_at'] = start_at
    query = \
        """
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
               t.start_at as date,
               case when home_id = %(player_id)s
               then w_svpt
               else l_svpt end as service_points,
               case when home_id = %(player_id)s
               then w_firstwon
               else l_firstwon end as firstwon,
               case when home_id = %(player_id)s
               then w_secondwon
               else l_secondwon end as secondwon,
               case when home_id = %(player_id)s
               then l_svpt
               else w_svpt end as opponen_service_points,
               case when home_id = %(player_id)s
               then l_firstwon
               else w_firstwon end as opponen_firstwon,
               case when home_id = %(player_id)s
               then l_secondwon
               else w_secondwon end as opponen_secondwon
            from %(match_table)s t inner join %(tour_table)s e on t.tour_id=e.id
            where (home_id=%(player_id)s or away_id=%(player_id)s)
               and surface ilike '%%%(surface)s%%'
               and round_name not ilike '%qualific%%'
               and t.start_at < date(%(start_at)s)
               ) a order by date desc limit 22
            ) s
        """
    df = pd.read_sql(query, connection, params=params)
    spw = df.iloc[0]['spw']
    rpw = df.iloc[0]['rpw']
    matches = df.iloc[0]['matches']
    return [spw, rpw, matches]
