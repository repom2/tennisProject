import logging
import os
import sys
import warnings
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
from django.db import connection
from django.utils import timezone
from psycopg2.extensions import AsIs
from tennisapi.ml.utils import (
    define_query_parameters,
    print_dataframe,
    probability_of_winning,
)
from tennisapi.models import Bet, BetWta, Match, Players, WtaMatch, WTAPlayers
from tennisapi.stats.analysis import match_analysis
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from tennisapi.stats.common_opponent import common_opponent
from tennisapi.stats.fatigue_modelling import fatigue_modelling
from tennisapi.stats.head2head import head2head
from tennisapi.stats.injury_modelling import injury_modelling
from tennisapi.stats.player_stats import player_stats
from tennisapi.stats.prob_by_serve.winning_match import matchProb

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


def probability_of_winning(x):
    l = (x) / 400
    prob2win = 1 / (1 + 10 ** (l))
    return 1 - prob2win


def get_data(params):
    query = """
        select 
                match_id,
                home_id,
                away_id,
                start_at,
                winner_first_name,
                loser_first_name,
                winner_name,
                loser_name,
                home_odds,
                away_odds,
                round_name,
                winner_grasselo,
                winner_hardelo,
                winner_clayelo,
                winner_games,
                winner_year_games,
                winner_year_elo,
                winner_year_grass_games,
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent,
                case when winner_year_grass_games = 0 then 0 else round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) end as winner_win_grass_percent,
                loser_grasselo,
                loser_hardelo,
                loser_clayelo,
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
                home_id,
                away_id,
                b.start_at,
                b.id as match_id,
                home_odds,
                away_odds,
                h.first_name as winner_first_name,
                aw.first_name as loser_first_name,
                h.last_name as winner_name,
                aw.last_name as loser_name,
                round_name,
                winner_code,
                (select elo from %(grass_elo)s el where el.player_id=home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_grasselo,
                (select elo from %(hard_elo)s el where el.player_id=home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_hardelo,
                (select elo from %(clay_elo)s el where el.player_id=home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_clayelo,
                (select count(*) from %(hard_elo)s c where c.player_id=home_id and c.date < date(b.start_at)) as winner_games,
                (select count(*) from %(hard_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.home_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_grass_games,
                (select elo from %(grass_elo)s el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_grasselo,
                (select elo from %(hard_elo)s el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,
                (select elo from %(clay_elo)s el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_clayelo,
                (select count(*) from %(hard_elo)s c where c.player_id=away_id and c.date < date(b.start_at)) as loser_games,
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
            where surface ilike '%%%(surface)s%%' and b.start_at between %(start_at)s and %(end_at)s
            ) 
            ss where winner_name is not null and loser_name is not null order by start_at
    """

    df = pd.read_sql(query, connection, params=params)

    return df


def label_round(data, mapping):
    data["round_name"] = data["round_name"].map(mapping)
    return data


def insert_data_to_match(level, tour):
    now = timezone.now().date()
    from_at = now  # - timedelta(days=3)
    end_at = now + timedelta(days=3)
    params, match_qs, bet_qs, player_qs, surface = define_query_parameters(
        level, tour, now, end_at
    )

    params["start_at"] = "2000-01-01"
    params["end_at"] = "2033-01-01"
    params["limit"] = 50
    data = get_data(params)

    l = len(data.index)
    if l == 0:
        log.info("No data")
        return

    if level == "atp":
        tour_spw, tour_rpw = 0.645, 0.355
    else:
        tour_spw, tour_rpw = 0.565, 0.435

    event_spw, event_rpw, tour_spw, tour_rpw = event_stats(params, level)
    if event_spw is None:
        if level == "atp":
            tour_spw, tour_rpw = 0.645, 0.355
        else:
            tour_spw, tour_rpw = 0.565, 0.435

    data[["spw1", "rpw1", "home_matches"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(player_stats, otypes=["O"])(
                data["home_id"], data["start_at"], params
            )
        ),
        index=data.index,
    )
    data[["spw2", "rpw2", "away_matches"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(player_stats, otypes=["O"])(
                data["away_id"], data["start_at"], params
            )
        ),
        index=data.index,
    )
    data["player1"] = data.apply(
        lambda x: (
            event_spw + (x.spw1 - tour_spw) - (x.rpw2 - tour_rpw)
            if (x.rpw2 and x.spw1)
            else None
        ),
        axis=1,
    )
    data["player2"] = data.apply(
        lambda x: (
            event_spw + (x.spw2 - tour_spw) - (x.rpw1 - tour_rpw)
            if (x.rpw1 and x.spw2)
            else None
        ),
        axis=1,
    )

    data["win"] = data.apply(
        lambda x: matchProb(
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

    # Common opponent
    data[["spw1_c", "spw2_c", "count"]] = pd.DataFrame(
        np.row_stack(
            np.vectorize(common_opponent, otypes=["O"])(
                params, data["home_id"], data["away_id"], event_spw, data["start_at"]
            )
        ),
        index=data.index,
    )

    data["win_c"] = data.apply(
        lambda x: matchProb(
            x.spw1_c, 1 - x.spw2_c, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3
        ),
        axis=1,
    ).round(2)

    data["f1"] = pd.DataFrame(
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
    data["f2"] = pd.DataFrame(
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
    data[["h2h", "c"]] = pd.DataFrame(
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
    data[["wo", "inj"]] = pd.DataFrame(
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
    data[["wo2", "inj2"]] = pd.DataFrame(
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

    data["odds1"] = data["home_odds"].astype(float)
    data["odds2"] = data["away_odds"].astype(float)

    data["prob"] = data["winner_hardelo"] - data["loser_hardelo"]
    data["prob_clay"] = data["winner_clayelo"] - data["loser_clayelo"]
    data["prob"] = data["prob"].apply(probability_of_winning).round(2)
    data["prob_clay"] = data["prob_clay"].apply(probability_of_winning).round(2)

    data["prob_year"] = data["winner_year_elo"] - data["loser_year_elo"]
    data["prob_y"] = data["prob_year"].apply(probability_of_winning).round(2)

    columns = [
        #'start_at',
        "winner_name",
        "loser_name",
        "odds1",
        "odds2",
        "prob",
        "prob_clay" "prob_y",
        "spw1",
        "rpw1",
        "spw2",
        "rpw2",
        "win",
        "f1",
        "f2",
        "h2h",
        "c",
        "wo",
        "inj",
        "wo2",
        "inj2",
        #'player1',
        #'player2',
        "win_c",
        "count",
        #'spw1_c',
        #'spw2_c',
        #'winner_hardelo',
        #'loser_hardelo',
    ]

    print("tour", tour_spw, tour_rpw)
    print("event", event_spw, event_rpw)
    data = data.replace(np.nan, None, regex=True)
    for index, row in data.iterrows():
        preview, reasoning = None, None  # match_analysis(row)
        bet_qs.update_or_create(
            match=match_qs.filter(id=row.match_id)[0],
            home=player_qs.filter(id=row.home_id)[0],
            away=player_qs.filter(id=row.away_id)[0],
            defaults={
                "start_at": row.start_at,
                "home_name": row.winner_name,
                "away_name": row.loser_name,
                "home_odds": row["odds1"],
                "away_odds": row["odds2"],
                "elo_prob_clay": row["prob_clay"],
                "elo_prob_hard": row["prob"],
                "year_elo_prob": row["prob_y"],
                "home_spw": row["spw1"],
                "home_rpw": row["rpw1"],
                "away_spw": row["spw2"],
                "away_rpw": row["rpw2"],
                "stats_win": row["win"],
                "home_fatigue": row["f1"],
                "away_fatigue": row["f2"],
                "h2h_win": row["h2h"],
                "h2h_matches": row["c"],
                "walkover_home": row["wo"],
                "walkover_away": row["wo2"],
                "home_inj_score": row["inj"],
                "away_inj_score": row["inj2"],
                "common_opponents": row["win_c"],
                "common_opponents_count": row["count"],
                "preview": preview,
                "reasoning": reasoning,
            },
        )
