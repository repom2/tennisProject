import warnings
import numpy as np
import pandas as pd
from django.db import connection
import os
from datetime import datetime, timedelta
from django.utils import timezone
import joblib
import logging
import sys
from tennisapi.stats.player_stats import player_stats
from tennisapi.stats.tennisabstract_site import tennisabstract_scrape
from tennisapi.stats.tennisabstract_site_atp import tennisabstract_scrape_atp
from tennisapi.stats.prob_by_serve.winning_match import matchProb, match_prob
from tennisapi.stats.fatigue_modelling import fatigue_modelling
from tennisapi.stats.injury_modelling import injury_modelling
from tennisapi.stats.head2head import head2head
from psycopg2.extensions import AsIs
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from tennisapi.stats.common_opponent import common_opponent
from tennisapi.stats.match_analysis import match_analysis
from tennisapi.stats.stats_analysis import stats_analysis
from tennisapi.models import (
    AtpMatches,
    Bet,
    Match,
    Players,
    WtaMatch,
    WTAPlayers,
    BetWta,
    AtpTour,
    WtaTour,
)
from tennisapi.ml.train_model import train_ml_model
import logging
from tabulate import tabulate

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def probability_of_winning(x):
    l = (x) / 400
    prob2win = 1 / (1 + 10 ** (l))
    return 1 - prob2win


def get_data(params):
    query = """
        select
                home_short_preview,
                home_spw,
                home_rpw,
                home_dr,
                home_matches,
                home_peak_rank,
                home_current_rank,
                home_plays,
                home_player_info,
                home_md_table,
                away_spw,
                away_rpw,
                away_dr,
                away_matches,
                away_peak_rank,
                away_current_rank,
                away_plays,
                away_player_info,
                away_md_table,
                match_id,
                home_id,
                away_id,
                home_player_id,
                away_player_id,
                start_at,
                home_fullname,
                away_fullname,
                case when atp_home_fullname is not null then atp_home_fullname 
                else TRIM(split_part(home_fullname, ',', 2)) || ' ' || TRIM(split_part(home_fullname, ',', 1)) end as atp_home_fullname,
                case when atp_away_fullname is not null then atp_away_fullname 
                else TRIM(split_part(away_fullname, ',', 2)) || ' ' || TRIM(split_part(away_fullname, ',', 1)) end as atp_away_fullname,
                case when winner_first_name is not null then 
                winner_first_name || ' ' || winner_name 
                else winner_name end as winner_fullname,
                case when loser_first_name is not null then 
                loser_first_name || ' ' || loser_name 
                else loser_name end as loser_fullname,
                winner_name,
                loser_name,
                home_odds,
                away_odds,
                round_name,
                case when (round_name ilike '%%ifinal%%' or round_name ilike '%%quarterfi%%') then 0
                    when (round_name ilike '%%r32%%' or round_name ilike '%%r16%%')  then 1 
                    when (round_name ilike '%%r64%%' or round_name ilike '%%r128%%')  then 2 
                else 3 end as round_code,
                winner_grasselo,
                winner_hardelo,
                winner_games,
                winner_year_games,
                winner_year_elo,
                winner_year_grass_games,
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent,
                case when winner_year_grass_games = 0 then 0 else round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) end as winner_win_grass_percent,
                loser_grasselo,
                loser_hardelo,
                loser_games,
                loser_year_games,
                loser_year_elo,
                loser_year_grass_games,
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent,
                case when loser_year_grass_games = 0 then 0 else round(loser_grass_win::numeric / loser_year_grass_games::numeric, 2) end as loser_win_grass_percent,
                case when winner_code = null then 10 else winner_code end,
                case when home_court_time is null then 0 else home_court_time / 60 end as home_court_time,
		        case when away_court_time is null then 0 else away_court_time / 60 end as away_court_time
            from (
            select
                home_short_preview,
                home_spw,
                home_rpw,
                home_dr,
                home_matches,
                home_peak_rank,
                home_current_rank,
                home_plays,
                home_player_info,
                home_md_table,
                away_spw,
                away_rpw,
                away_dr,
                away_matches,
                away_peak_rank,
                away_current_rank,
                away_plays,
                away_player_info,
                away_md_table,
                b.home_id,
                b.away_id,
                b.start_at,
                b.id as match_id,
                h.name_full as home_fullname,
                aw.name_full as away_fullname,
                h.atp_name_full as atp_home_fullname,
                aw.atp_name_full as atp_away_fullname,
                h.player_id as home_player_id,
                aw.player_id as away_player_id,
                b.home_odds,
                b.away_odds,
                h.first_name as winner_first_name,
                aw.first_name as loser_first_name,
                h.last_name as winner_name,
                aw.last_name as loser_name,
                round_name,
                winner_code,
                (select elo from %(grass_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_grasselo,
                (select elo from %(hard_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_hardelo,
                (select count(*) from %(hard_elo)s c where c.player_id=b.home_id and c.date < date(b.start_at)) as winner_games,
                (select count(*) from %(hard_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.home_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_grass_games,
                (select elo from %(grass_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_grasselo,
                (select elo from %(hard_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,
                (select count(*) from %(hard_elo)s c where c.player_id=b.away_id and c.date < date(b.start_at)) as loser_games,
                (select count(*) from %(hard_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.away_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_grass_games,
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(hard_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_win,
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(grass_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_grass_win,
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(hard_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_win,
            (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(grass_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_grass_win,
                (select sum(court_time) from %(match_table)s c
                where c.start_at between (b.start_at - interval '14 days') and c.start_at and
                c.start_at < b.start_at and (c.home_id=b.home_id or c.away_id=b.home_id)) as home_court_time,
                (select sum(court_time) from %(match_table)s c
                where c.start_at between (b.start_at - interval '14 days') and c.start_at and
                c.start_at < b.start_at and (c.home_id=b.away_id or c.away_id=b.away_id)) as away_court_time
            from %(match_table)s b
            left join %(player_table)s h on h.id = b.home_id
            left join %(player_table)s aw on aw.id = b.away_id
            left join %(bet_table)s bet on bet.match_id = b.id
            where b.surface ilike '%%%(surface)s%%' and b.start_at between %(start_at)s and %(end_at)s
            and (
            (tourney_name ilike '%%%(tour)s%%' ))
            ) 
            ss where winner_name is not null and loser_name is not null order by start_at
    """

    df = pd.read_sql(query, connection, params=params)

    return df


def label_round(data, mapping):
    data["round_name"] = data["round_name"].map(mapping)
    return data


def predict_ta(level, tour):
    now = timezone.now().date()
    end_at = now + timedelta(days=2)
    from_at = now - timedelta(days=2)

    if level == "atp":
        qs =(
            Match.objects.filter(tourney_name__icontains=tour, start_at__gte=from_at)
            .values_list("surface", flat=True)
            .first()
        )
        if 'clay' in qs or 'Clay' in qs:
            surface = 'clay'
        elif 'grass' in qs or 'Grass' in qs:
            surface = 'grass'
        elif 'hard' in qs or 'Hard' in qs:
            surface = 'hard'
        else:
            logging.info("Surface not found: %s", qs)

        bet_qs = Bet.objects.all()
        match_qs = Match.objects.all()
        player_qs = Players.objects.all()
        tour_table = "tennisapi_atptour"
        matches_table = "tennisapi_atpmatches"
        match_table = "tennisapi_match"
        player_table = "tennisapi_players"
        hard_elo = "tennisapi_atphardelo"
        grass_elo = "tennisapi_atpgrasselo"
        clay_elo = "tennisapi_atpelo"
        bet_table = "tennisapi_bet"
        if surface == "clay":
            hard_elo = clay_elo
    else:
        qs =(
            WtaMatch.objects.filter(tourney_name__icontains=tour, start_at__gte=from_at)
            .values_list("surface", flat=True)
            .first()
        )
        if 'clay' in qs or 'Clay' in qs:
            surface = 'clay'
        elif 'grass' in qs or 'Grass' in qs:
            surface = 'grass'
        elif 'hard' in qs or 'Hard' in qs:
            surface = 'hard'
        else:
            logging.info("Surface not found: %s", qs)
        logging.info("Surface: %s", surface)

        bet_qs = BetWta.objects.all()
        match_qs = WtaMatch.objects.all()
        player_qs = WTAPlayers.objects.all()
        tour_table = "tennisapi_wtatour"
        matches_table = "tennisapi_wtamatches"
        match_table = "tennisapi_wtamatch"
        player_table = "tennisapi_wtaplayers"
        hard_elo = "tennisapi_wtahardelo"
        grass_elo = "tennisapi_wtagrasselo"
        clay_elo = "tennisapi_wtaclayelo"
        bet_table = "tennisapi_betwta"
    params = {
        "tour_table": AsIs(tour_table),
        "matches_table": AsIs(matches_table),
        "player_table": AsIs(player_table),
        "match_table": AsIs(match_table),
        "hard_elo": AsIs(hard_elo),
        "grass_elo": AsIs(grass_elo),
        "clay_elo": AsIs(clay_elo),
        "tour": AsIs(tour),
        "start_at": now,
        "end_at": end_at,
        "surface": AsIs(surface),
        "bet_table": AsIs(bet_table),
    }
    data = get_data(params)

    #data = data[(data["home_player_id"] == 211095) ]
    #data = data.iloc[1:]

    l = len(data.index)
    if l == 0:
        print("No data")
        return

    columns = [
        "start_at",
        "winner_fullname",
        "loser_fullname",
        #'home_id',
        #'away_id',
        "home_player_id",
        "away_player_id",
        "home_fullname",
        "away_fullname",
        "atp_home_fullname",
        "atp_away_fullname",
    ]

    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
    )

    if level == "atp":
        tour_spw, tour_rpw = 0.645, 0.355
    else:
        tour_spw, tour_rpw = 0.565, 0.435

    date = "2015-1-1"
    params = {
        "event": AsIs(tour),
        "surface": AsIs(surface),
        "tour_table": AsIs(tour_table),
        "matches_table": AsIs(matches_table),
        "date": date,
    }
    event_spw, event_rpw = event_stats(params)

    if event_spw is None:
        if level == "atp":
            event_spw, tour_spw, tour_rpw = 0.645, 0.645, 0.355
        else:
            event_spw, tour_spw, tour_rpw = 0.565, 0.565, 0.435
    logging.info(f"Event SPW: {event_spw}, Event RPW: {event_rpw}")
    logging.info(f"Tour SPW: {tour_spw}, Tour RPW: {tour_rpw}")

    if level == "atp":
        data[
            [
                "home_spw",
                "home_rpw",
                "home_dr",
                "home_matches",
                "home_peak_rank",
                "home_current_rank",
                "home_plays",
                "home_player_info",
                "home_md_table",
                "home_spw_clay",
                "home_rpw_clay",
                "home_dr_clay",
                "home_matches_clay",
            ]
        ] = data.apply(
            lambda row: tennisabstract_scrape_atp(row, 'home', surface),
            axis=1)
        data[
            [
                "away_spw",
                "away_rpw",
                "away_dr",
                "away_matches",
                "away_peak_rank",
                "away_current_rank",
                "away_plays",
                "away_player_info",
                "away_md_table",
                "away_spw_clay",
                "away_rpw_clay",
                "away_dr_clay",
                "away_matches_clay",
            ]
        ] = data.apply(
            lambda row: tennisabstract_scrape_atp(row, 'away', surface),
            axis=1)
    else:
        data[
            [
                "home_spw",
                "home_rpw",
                "home_dr",
                "home_matches",
                "home_peak_rank",
                "home_current_rank",
                "home_plays",
                "home_player_info",
                "home_md_table",
                "home_spw_clay",
                "home_rpw_clay",
                "home_dr_clay",
                "home_matches_clay",
            ]
        ] = data.apply(
            lambda row: tennisabstract_scrape(row, 'home', surface),
            axis=1)
        data[
            [
                "away_spw",
                "away_rpw",
                "away_dr",
                "away_matches",
                "away_peak_rank",
                "away_current_rank",
                "away_plays",
                "away_player_info",
                "away_md_table",
                "away_spw_clay",
                "away_rpw_clay",
                "away_dr_clay",
                "away_matches_clay",
            ]
        ] = data.apply(
            lambda row: tennisabstract_scrape(row, 'away', surface),
            axis=1)

    data["home_spw"] = data["home_spw"].astype(float)
    data["home_rpw"] = data["home_rpw"].astype(float)
    data["home_dr"] = data["home_dr"].astype(float)
    data["away_spw"] = data["away_spw"].astype(float)
    data["away_rpw"] = data["away_rpw"].astype(float)
    data["away_dr"] = data["away_dr"].astype(float)
    data["home_spw_clay"] = data["home_spw_clay"].astype(float)
    data["home_rpw_clay"] = data["home_rpw_clay"].astype(float)
    data["home_dr_clay"] = data["home_dr_clay"].astype(float)
    data["away_spw_clay"] = data["away_spw_clay"].astype(float)
    data["away_rpw_clay"] = data["away_rpw_clay"].astype(float)
    data["away_dr_clay"] = data["away_dr_clay"].astype(float)
    data["player1"] = data.apply(
        lambda x: tour_spw + (x.home_spw - tour_spw) - (x.away_rpw - tour_rpw)
        if (x.away_rpw and x.home_spw)
        else None,
        axis=1,
    )
    data["player2"] = data.apply(
        lambda x: tour_spw + (x.away_spw - tour_spw) - (x.home_rpw - tour_rpw)
        if (x.home_rpw and x.away_spw)
        else None,
        axis=1,
    )
    data["player1_clay"] = data.apply(
        lambda x: tour_spw + (x.home_spw_clay - tour_spw) - (x.away_rpw_clay - tour_rpw)
        if (x.away_rpw_clay and x.home_spw_clay)
        else None,
        axis=1,
    )
    data["player2_clay"] = data.apply(
        lambda x: tour_spw + (x.away_spw_clay - tour_spw) - (x.home_rpw_clay - tour_rpw)
        if (x.home_rpw_clay and x.away_spw_clay)
        else None,
        axis=1,
    )
    columns = [
        "player1_clay", "player2_clay",
    ]
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
    )
    cols = [
        "atp_home_fullname",
        "atp_away_fullname",
        "home_spw",
        "home_rpw",
        "home_dr",
        "away_spw",
        "away_rpw",
        "away_dr",
        "player1",
        "player2",
    ]
    logging.info(
        f"DataFrame:\n{tabulate(data[cols], headers='keys', tablefmt='psql', showindex=True)}"
    )
    # Away player stats win
    data[
        [
            "stats_win",
            "away_wins_single_game",
            "away_wins_single_set",
            "away_wins_1_set",
            "away_wins_2_set",
            "away_ah_7_5",
            "away_ah_6_5",
            "away_ah_5_5",
            "away_ah_4_5",
            "away_ah_3_5",
            "away_ah_2_5",
            "games_over_21_5",
            "games_over_22_5",
            "games_over_23_5",
            "games_over_24_5",
            "games_over_25_5",
        ]
        ] = data.apply(
        lambda x: match_prob(
            x.player2 if x.player2 else None,
            1 - x.player1 if x.player1 else None,
            gv=0,
            gw=0,
            sv=0,
            sw=0,
            mv=0,
            mw=0,
            sets=3,
        ),
        axis=1,
    ).round(2)
    # Home player stats win
    data[
        [
            "stats_win",
            "home_wins_single_game",
            "home_wins_single_set",
            "home_wins_1_set",
            "home_wins_2_set",
            "home_ah_7_5",
            "home_ah_6_5",
            "home_ah_5_5",
            "home_ah_4_5",
            "home_ah_3_5",
            "home_ah_2_5",
            "games_over_21_5",
            "games_over_22_5",
            "games_over_23_5",
            "games_over_24_5",
            "games_over_25_5",
        ]
        ] = data.apply(
        lambda x: match_prob(
            x.player1 if x.player1 else None,
            1 - x.player2 if x.player2 else None,
            gv=0,
            gw=0,
            sv=0,
            sw=0,
            mv=0,
            mw=0,
            sets=3,
        ),
        axis=1,
    ).round(2)
    data[
        [
            "stats_win_clay",
            "home_wins_single_game",
            "home_wins_single_set",
            "home_wins_1_set",
            "home_wins_2_set",
            "home_ah_7_5",
            "home_ah_6_5",
            "home_ah_5_5",
            "home_ah_4_5",
            "home_ah_3_5",
            "home_ah_2_5",
            "games_over_21_5",
            "games_over_22_5",
            "games_over_23_5",
            "games_over_24_5",
            "games_over_25_5",
        ]
        ] = data.apply(
        lambda x: match_prob(
            x.player1_clay if x.player1_clay else None,
            1 - x.player2_clay if x.player2_clay else None,
            gv=0,
            gw=0,
            sv=0,
            sw=0,
            mv=0,
            mw=0,
            sets=3,
        ),
        axis=1,
    ).round(2)
    columns = [
        "stats_win_clay",
    ]
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
    )

    # Common opponent
    data[["spw1_c", "spw2_c", "common_opponents_count"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(common_opponent, otypes=["O"])(
                params, data["home_id"], data["away_id"], event_spw, data["start_at"]
            )
        ),
        index=data.index,
    )

    data["common_opponents"] = data.apply(
        lambda x: matchProb(
            x.spw1_c, 1 - x.spw2_c, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3
        ),
        axis=1,
    ).round(2)

    data["home_fatigue"] = pd.DataFrame(
        np.row_stack(
            np.vectorize(fatigue_modelling, otypes=["O"])(
                data["home_id"],
                params["tour_table"],
                params["matches_table"],
                params["start_at"],
            )
        ),
        index=data.index,
    )
    data["away_fatigue"] = pd.DataFrame(
        np.row_stack(
            np.vectorize(fatigue_modelling, otypes=["O"])(
                data["away_id"],
                params["tour_table"],
                params["matches_table"],
                params["start_at"],
            )
        ),
        index=data.index,
    )
    data[["h2h_win", "h2h_matches"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(head2head, otypes=["O"])(
                data["home_id"],
                data["away_id"],
                params["tour_table"],
                params["matches_table"],
                params["start_at"],
            )
        ),
        index=data.index,
    )
    data["date"] = data["start_at"].dt.strftime("%Y-%m-%d")
    data[["walkover_home", "home_inj_score"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(injury_modelling, otypes=["O"])(
                data["date"],
                data["home_id"],
                params["tour_table"],
                params["matches_table"],
            )
        ),
        index=data.index,
    )
    data[["walkover_away", "away_inj_score"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(injury_modelling, otypes=["O"])(
                data["date"],
                data["away_id"],
                params["tour_table"],
                params["matches_table"],
            )
        ),
        index=data.index,
    )

    data["home_odds"] = data["home_odds"].astype(float)
    data["away_odds"] = data["away_odds"].astype(float)

    data["elo_prob"] = data["winner_hardelo"] - data["loser_hardelo"]
    data["elo_prob"] = data["elo_prob"].apply(probability_of_winning).round(2)

    data["year_elo_prob"] = data["winner_year_elo"] - data["loser_year_elo"]
    data["year_elo_prob"] = data["year_elo_prob"].apply(probability_of_winning).round(2)

    print("tour", tour_spw, tour_rpw)
    print("event", event_spw, event_rpw)
    # data = data.where(pd.notnull(data), None)
    data = data.replace(np.nan, None, regex=True)
    for index, row in data.iterrows():
        try:
            home_prob, away_prob, home_yield, away_yield = train_ml_model(
                row, level, params, surface
            )
        except Exception as e:
            log.error(e)
            continue
        """home_preview, home_short_preview = match_analysis(
            row.winner_name,
            row.loser_name,
            row.home_player_info,
            row.home_md_table,
            event_spw,
            event_rpw,
            tour_spw,
            tour_rpw,
        )
        away_preview, away_short_preview = match_analysis(
            row.loser_name,
            row.winner_name,
            row.away_player_info,
            row.away_md_table,
            event_spw,
            event_rpw,
            tour_spw,
            tour_rpw,
        )"""
        if row.home_short_preview is None:
            log.info("No short preview")
            log.info(row.home_short_preview)
            home_short_preview = stats_analysis(
                row.winner_name,
                row.loser_name,
                row.home_player_info,
                row.away_player_info,
                row.home_md_table,
                row.away_md_table,
                row.stats_win,
                row.elo_prob,
                row.home_matches,
                row.away_matches,
            )
        else:
            home_short_preview = row.home_short_preview
        home_preview, away_preview, away_short_preview = None, None, None
        try:
            row["home_current_rank"] = int(row["home_current_rank"])
        except ValueError:
            row["home_current_rank"] = None
        try:
            row["away_current_rank"] = int(row["away_current_rank"])
        except ValueError:
            row["away_current_rank"] = None
        bet_qs.update_or_create(
            match=match_qs.filter(id=row.match_id)[0],
            home=player_qs.filter(id=row.home_id)[0],
            away=player_qs.filter(id=row.away_id)[0],
            defaults={
                "start_at": row.start_at,
                "home_name": row.winner_name,
                "away_name": row.loser_name,
                "home_odds": row["home_odds"],
                "away_odds": row["away_odds"],
                "elo_prob": row["elo_prob"],
                "year_elo_prob": row["year_elo_prob"],
                "home_spw": row["home_spw"],
                "home_rpw": row["home_rpw"],
                "away_spw": row["away_spw"],
                "away_rpw": row["away_rpw"],
                "stats_win": row["stats_win"],
                "home_fatigue": row["home_fatigue"],
                "away_fatigue": row["away_fatigue"],
                "h2h_win": row["h2h_win"],
                "h2h_matches": row["h2h_matches"],
                "walkover_home": row["walkover_home"],
                "walkover_away": row["walkover_away"],
                "home_inj_score": row["home_inj_score"],
                "away_inj_score": row["away_inj_score"],
                "common_opponents": row["common_opponents"],
                "common_opponents_count": row["common_opponents_count"],
                # "preview": preview,
                # "reasoning": reasoning,
                "home_prob": home_prob,
                "away_prob": away_prob,
                "home_yield": home_yield,
                "away_yield": away_yield,
                "home_dr": row["home_dr"],
                "away_dr": row["away_dr"],
                "home_peak_rank": row["home_peak_rank"],
                "away_peak_rank": row["away_peak_rank"],
                "home_current_rank": row["home_current_rank"],
                "away_current_rank": row["away_current_rank"],
                "home_plays": row["home_plays"],
                "away_plays": row["away_plays"],
                "home_matches": row["home_matches"],
                "away_matches": row["away_matches"],
                "home_player_info": row["home_player_info"],
                "away_player_info": row["away_player_info"],
                "home_md_table": row["home_md_table"],
                "away_md_table": row["away_md_table"],
                "home_preview": home_preview,
                "home_short_preview": home_short_preview,
                "away_preview": away_preview,
                "away_short_preview": away_short_preview,
                "home_wins_single_game": row["home_wins_single_game"],
                "home_wins_single_set": row["home_wins_single_set"],
                "home_wins_1_set": row["home_wins_1_set"],
                "home_wins_2_set": row["home_wins_2_set"],
                "home_ah_7_5": row["home_ah_7_5"],
                "home_ah_6_5": row["home_ah_6_5"],
                "home_ah_5_5": row["home_ah_5_5"],
                "home_ah_4_5": row["home_ah_4_5"],
                "home_ah_3_5": row["home_ah_3_5"],
                "home_ah_2_5": row["home_ah_2_5"],
                "away_ah_7_5": row["away_ah_7_5"],
                "away_ah_6_5": row["away_ah_6_5"],
                "away_ah_5_5": row["away_ah_5_5"],
                "away_ah_4_5": row["away_ah_4_5"],
                "away_ah_3_5": row["away_ah_3_5"],
                "away_ah_2_5": row["away_ah_2_5"],
                "games_over_21_5": row["games_over_21_5"],
                "games_over_22_5": row["games_over_22_5"],
                "games_over_23_5": row["games_over_23_5"],
                "games_over_24_5": row["games_over_24_5"],
                "games_over_25_5": row["games_over_25_5"],
                "stats_win_clay": row["stats_win_clay"],
                "home_spw_clay": row["home_spw_clay"],
                "home_rpw_clay": row["home_rpw_clay"],
                "home_dr_clay": row["home_dr_clay"],
                "home_matches_clay": row["home_matches_clay"],
                "away_spw_clay": row["away_spw_clay"],
                "away_rpw_clay": row["away_rpw_clay"],
                "away_dr_clay": row["away_dr_clay"],
                "away_matches_clay": row["away_matches_clay"],
                "surface": surface,
            },
        )
