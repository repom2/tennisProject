import logging

import pandas as pd
from django.db import connection

log = logging.getLogger(__name__)


def event_stats(params, level):
    query = """
            select 
                *, 
                (SPW + loser_SPW) / 2 as avg_SPW,
                (RPW + loser_RPW) / 2 as avg_RPW,
                (DR + loser_DR) / 2 as avg_DR
            from (select
                round(avg(
                    case when SPW is not null and SPW > 0.17 then SPW  when SPW2 is not null and SPW2 > 0.17 then SPW2 else null end
                ), 2) as SPW,
                round(avg(
                    case when loser_SPW is not null and loser_SPW> 0.17 then loser_SPW when loser_SPW2 is not null and loser_SPW2> 0.17 then loser_SPW2 else null end
                ), 2) as loser_SPW,
                round(avg(
                    case when RPW is not null and RPW > 0.17 then RPW  when RPW2 is not null and RPW2 > 0.17 then RPW2 else null end
                ), 2) as RPW,
                round(avg(
                    case when loser_RPW is not null and loser_RPW > 0.17 then loser_RPW  when loser_RPW2 is not null and loser_RPW2 > 0.17 then loser_RPW2 else null end
                    ), 2) as loser_RPW,
                round(avg(RPW)/ avg(loser_RPW),2) as DR,
                round(avg(loser_RPW)/(avg(RPW)),2) as loser_DR
            from (
            select
                (firstwon + secondwon) / nullif(service_points::numeric, 0) as SPW2,
                (opponent_firstwon + opponent_secondwon) / nullif(opponent_service_points::numeric, 0) as loser_SPW2,
                (opponent_service_points - opponent_firstwon - opponent_secondwon) / nullif(opponent_service_points::numeric, 0) as RPW2,
                (service_points - firstwon - secondwon) / nullif(service_points::numeric, 0) as loser_RPW2,
                service_points - firstwon - secondwon as service_points_lost,
                opponent_service_points - opponent_firstwon - opponent_secondwon as return_points_won,
                round((winner_service_points_won) / nullif(service_points::numeric, 0), 2) as SPW,
                round((loser_service_points_won) / nullif(opponent_service_points::numeric, 0), 2) as loser_SPW,
                round((winner_receiver_points_won) / nullif(opponent_service_points::numeric, 0), 2) as RPW,
                round((loser_receiver_points_won) / nullif(service_points::numeric, 0), 2) as loser_RPW
            from (
            select
                t.date,
                w_svpt as service_points, \
                w_firstwon as firstwon,
                w_secondwon as secondwon,
                l_svpt as opponent_service_points,
                l_firstwon as opponent_firstwon,
                l_secondwon as opponent_secondwon,
                winner_service_points_won,
                loser_service_points_won,
                winner_receiver_points_won,
                loser_receiver_points_won
            from  %(matches_table)s t
            where
                surface ilike '%%%(surface)s%%' and
                (tourney_name ilike '%%%(tourney_name)s%%' ) and
                tour_id ilike '%%%(event_id)s%%' and
                t.date > %(date)s
            ) a 
            ) s ) aa; 
    """

    df = pd.read_sql(query, connection, params=params)
    avg_spw = df.iloc[0]["avg_spw"]
    avg_rpw = df.iloc[0]["avg_rpw"]

    if level == "atp":
        tour_spw, tour_rpw = 0.645, 0.355
    else:
        tour_spw, tour_rpw = 0.565, 0.435

    if avg_spw is None or avg_rpw is None:
        log.info(f"Event SPW: {avg_spw}, Event RPW: {avg_rpw}")
        # exit()
        if level == "atp":
            avg_spw, tour_spw, tour_rpw = 0.645, 0.645, 0.355
        else:
            avg_spw, tour_spw, tour_rpw = 0.565, 0.565, 0.435
    logging.info(f"Event SPW: {avg_spw}, Event RPW: {avg_rpw}")
    logging.info(f"Tour SPW: {tour_spw}, Tour RPW: {tour_rpw}")

    return avg_spw, avg_rpw, tour_spw, tour_rpw
