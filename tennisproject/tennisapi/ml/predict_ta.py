import copy
import logging
import time
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
from django.utils import timezone
from tabulate import tabulate
from tennisapi.ml.get_data import get_data
from tennisapi.ml.train_model import train_ml_model
from tennisapi.ml.utils import (
    define_query_parameters,
    print_dataframe,
    probability_of_winning,
)
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from tennisapi.stats.common_opponent import common_opponent
from tennisapi.stats.fatigue_modelling import fatigue_modelling
from tennisapi.stats.head2head import head2head
from tennisapi.stats.injury_modelling import injury_modelling
from tennisapi.stats.match_analysis import match_analysis
from tennisapi.stats.player_stats import player_stats
from tennisapi.stats.prob_by_serve.winning_match import match_prob, matchProb
from tennisapi.stats.stats_analysis import stats_analysis
from tennisapi.stats.tennisabstract_site import tennisabstract_scrape
from tennisapi.stats.tennisabstract_site_atp import tennisabstract_scrape_atp

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def predict_ta(level, tour):
    if level == "atp":
        sets = 3
    else:
        sets = 3
    use_scrape = True
    now = timezone.now().date()
    from_at = now  # - timedelta(days=1)
    end_at = now + timedelta(days=3)
    params, match_qs, bet_qs, player_qs, surface = define_query_parameters(
        level, tour, from_at, end_at
    )
    data = get_data(params)

    columns = [
        # "start_at",
        "winner_fullname",
        "loser_fullname",
        # "home_player_id",
        # "away_player_id",
    ]
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
    )

    data_copy = copy.deepcopy(data)

    event_spw, event_rpw, tour_spw, tour_rpw = event_stats(params, level)

    for i in range(0, 30):
        time.sleep(4)
        data = data_copy.iloc[i : i + 1]

        if len(data.index) == 0:
            print("No data")
            return

        stats_params = params
        stats_params["start_at"] = "2023-01-01"
        stats_params["limit"] = 52

        data[["home_spw", "home_rpw", "home_matches"]] = pd.DataFrame(
            np.row_stack(
                np.vectorize(player_stats, otypes=["O"])(
                    data["home_id"], data["start_at"], stats_params
                )
            ),
            index=data.index,
        )
        data[["away_spw", "away_rpw", "away_matches"]] = pd.DataFrame(
            np.row_stack(
                np.vectorize(player_stats, otypes=["O"])(
                    data["away_id"], data["start_at"], stats_params
                )
            ),
            index=data.index,
        )
        data["player1"] = data.apply(
            lambda x: (
                tour_spw + (x.home_spw - tour_spw) - (x.away_rpw - tour_rpw)
                if (x.away_rpw and x.home_spw)
                else None
            ),
            axis=1,
        )
        data["player2"] = data.apply(
            lambda x: (
                tour_spw + (x.away_spw - tour_spw) - (x.home_rpw - tour_rpw)
                if (x.home_rpw and x.away_spw)
                else None
            ),
            axis=1,
        )
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
                x.player1 if x.player1 else 0,
                1 - x.player2 if x.player2 else 0,
                gv=0,
                gw=0,
                sv=0,
                sw=0,
                mv=0,
                mw=0,
                sets=sets,
            ),
            axis=1,
        ).round(
            2
        )
        columns = [
            "winner_fullname",
            "loser_fullname",
            "stats_win",
            "home_matches",
            "away_matches",
        ]
        # logging.info(
        #   f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}")
        # exit()

        if use_scrape:
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
                        "home_spw_grass",
                        "home_rpw_grass",
                        "home_dr_grass",
                        "home_matches_grass",
                    ]
                ] = data.apply(
                    lambda row: tennisabstract_scrape_atp(row, "home", surface), axis=1
                )
                time.sleep(4)
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
                        "away_spw_grass",
                        "away_rpw_grass",
                        "away_dr_grass",
                        "away_matches_grass",
                    ]
                ] = data.apply(
                    lambda row: tennisabstract_scrape_atp(row, "away", surface), axis=1
                )
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
                        "home_spw_grass",
                        "home_rpw_grass",
                        "home_dr_grass",
                        "home_matches_grass",
                    ]
                ] = data.apply(
                    lambda row: tennisabstract_scrape(row, "home", surface), axis=1
                )
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
                        "away_spw_grass",
                        "away_rpw_grass",
                        "away_dr_grass",
                        "away_matches_grass",
                    ]
                ] = data.apply(
                    lambda row: tennisabstract_scrape(row, "away", surface), axis=1
                )
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
                    "home_spw_grass",
                    "home_rpw_grass",
                    "home_dr_grass",
                    "home_matches_grass",
                ]
            ] = None
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
                    "away_spw_grass",
                    "away_rpw_grass",
                    "away_dr_grass",
                    "away_matches_grass",
                ]
            ] = None
        data["player1"] = data.apply(
            lambda x: (
                tour_spw + (x.home_spw - tour_spw) - (x.away_rpw - tour_rpw)
                if (x.away_rpw and x.home_spw)
                else None
            ),
            axis=1,
        )
        data["player2"] = data.apply(
            lambda x: (
                tour_spw + (x.away_spw - tour_spw) - (x.home_rpw - tour_rpw)
                if (x.home_rpw and x.away_spw)
                else None
            ),
            axis=1,
        )
        data["player1_clay"] = data.apply(
            lambda x: (
                tour_spw + (x.home_spw_clay - tour_spw) - (x.away_rpw_clay - tour_rpw)
                if (x.away_rpw_clay and x.home_spw_clay)
                else None
            ),
            axis=1,
        )
        data["player2_clay"] = data.apply(
            lambda x: (
                tour_spw + (x.away_spw_clay - tour_spw) - (x.home_rpw_clay - tour_rpw)
                if (x.home_rpw_clay and x.away_spw_clay)
                else None
            ),
            axis=1,
        )
        data["player1_grass"] = data.apply(
            lambda x: (
                tour_spw + (x.home_spw_grass - tour_spw) - (x.away_rpw_grass - tour_rpw)
                if (x.away_rpw_grass and x.home_spw_grass)
                else None
            ),
            axis=1,
        )
        data["player2_grass"] = data.apply(
            lambda x: (
                tour_spw + (x.away_spw_grass - tour_spw) - (x.home_rpw_grass - tour_rpw)
                if (x.home_rpw_grass and x.away_spw_grass)
                else None
            ),
            axis=1,
        )
        columns = ["player1", "player2"]
        # logging.info(
        #   f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
        # )
        # exit()
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
        # logging.info(
        #   f"DataFrame:\n{tabulate(data[cols], headers='keys', tablefmt='psql', showindex=True)}"
        # )
        if surface == "clay":
            stats_win_field = "stats_win_clay"
            elo_prob_field = "elo_prob_clay"
        elif surface == "grass":
            stats_win_field = "stats_win_grass"
            elo_prob_field = "elo_prob_grass"
        else:
            stats_win_field = "stats_win_hard"
            elo_prob_field = "elo_prob_hard"
        # Away player stats win
        data[
            [
                "stats_win_hard",
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
                x.player1 if x.player1 else 0,
                1 - x.player2 if x.player2 else 0,
                gv=0,
                gw=0,
                sv=0,
                sw=0,
                mv=0,
                mw=0,
                sets=sets,
            ),
            axis=1,
        ).round(
            2
        )
        # Home player stats win
        data[
            [
                "stats_win_hard",
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
                x.player1 if x.player1 else 0,
                1 - x.player2 if x.player2 else 0,
                gv=0,
                gw=0,
                sv=0,
                sw=0,
                mv=0,
                mw=0,
                sets=sets,
            ),
            axis=1,
        ).round(
            2
        )
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
                x.player1_clay if x.player1_clay else 0,
                1 - x.player2_clay if x.player2_clay else 0,
                gv=0,
                gw=0,
                sv=0,
                sw=0,
                mv=0,
                mw=0,
                sets=sets,
            ),
            axis=1,
        ).round(
            2
        )
        data[
            [
                "stats_win_grass",
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
                x.player1_grass if x.player1_grass else 0,
                1 - x.player2_grass if x.player2_grass else 0,
                gv=0,
                gw=0,
                sv=0,
                sw=0,
                mv=0,
                mw=0,
                sets=sets,
            ),
            axis=1,
        ).round(
            2
        )
        columns = ["stats_win_clay", "stats_win_grass", "stats_win_hard"]
        # logging.info(
        #   f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
        # )
        # Common opponent
        data[["spw1_c", "spw2_c", "common_opponents_count"]] = pd.DataFrame(
            np.row_stack(
                np.vectorize(common_opponent, otypes=["O"])(
                    params,
                    data["home_id"],
                    data["away_id"],
                    event_spw,
                    data["start_at"],
                )
            ),
            index=data.index,
        )
        if level == "atp":
            sets = 3
        else:
            sets = 3
        data["common_opponents"] = data.apply(
            lambda x: matchProb(
                x.spw1_c, 1 - x.spw2_c, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=sets
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

        data["elo_prob_hard"] = data["winner_hardelo"] - data["loser_hardelo"]
        data["elo_prob_hard"] = (
            data["elo_prob_hard"].apply(probability_of_winning).round(2)
        )

        data["elo_prob_clay"] = data["winner_clayelo"] - data["loser_clayelo"]
        data["elo_prob_clay"] = (
            data["elo_prob_clay"].apply(probability_of_winning).round(2)
        )

        data["elo_prob_grass"] = data["winner_grasselo"] - data["loser_grasselo"]
        data["elo_prob_grass"] = (
            data["elo_prob_grass"].apply(probability_of_winning).round(2)
        )

        data["year_elo_prob"] = data["winner_year_elo"] - data["loser_year_elo"]
        data["year_elo_prob"] = (
            data["year_elo_prob"].apply(probability_of_winning).round(2)
        )
        # data = data.where(pd.notnull(data), None)
        data = data.replace(np.nan, None, regex=True)
        for index, row in data.iterrows():
            # try:
            home_prob, away_prob, home_yield, away_yield = train_ml_model(
                row, level, params, surface, stats_win_field, elo_prob_field
            )
            # except Exception as e:
            #   log.error(e)
            #  continue
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
            )
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
                    row.elo_prob_hard,
                    row.home_matches,
                    row.away_matches,
                )
            else:
                home_short_preview = row.home_short_preview"""
            home_short_preview = None
            home_preview, away_preview, away_short_preview = None, None, None
            try:
                row["home_current_rank"] = int(row["home_current_rank"])
            except (ValueError, TypeError):
                row["home_current_rank"] = None
            try:
                row["away_current_rank"] = int(row["away_current_rank"])
            except (ValueError, TypeError):
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
                    "elo_prob_hard": row["elo_prob_hard"],
                    "elo_prob_clay": row["elo_prob_clay"],
                    "elo_prob_grass": row["elo_prob_grass"],
                    "year_elo_prob": row["year_elo_prob"],
                    "home_spw": row["home_spw"],
                    "home_rpw": row["home_rpw"],
                    "away_spw": row["away_spw"],
                    "away_rpw": row["away_rpw"],
                    "home_spw_clay": row["home_spw_clay"],
                    "home_rpw_clay": row["home_rpw_clay"],
                    "away_spw_clay": row["away_spw_clay"],
                    "away_rpw_clay": row["away_rpw_clay"],
                    "home_spw_grass": row["home_spw_grass"],
                    "home_rpw_grass": row["home_rpw_grass"],
                    "away_spw_grass": row["away_spw_grass"],
                    "away_rpw_grass": row["away_rpw_grass"],
                    "stats_win": row["stats_win"],
                    "stats_win_hard": row["stats_win_hard"],
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
                    "stats_win_grass": row["stats_win_grass"],
                    "home_dr_clay": row["home_dr_clay"],
                    "home_matches_clay": row["home_matches_clay"],
                    "away_dr_clay": row["away_dr_clay"],
                    "away_matches_clay": row["away_matches_clay"],
                    "home_dr_grass": row["home_dr_grass"],
                    "home_matches_grass": row["home_matches_grass"],
                    "away_dr_grass": row["away_dr_grass"],
                    "away_matches_grass": row["away_matches_grass"],
                    "surface": params["surface"],
                    "home_elo_hard": row["winner_hardelo"],
                    "home_elo_hard_games": row["winner_hardelo_games"],
                    "away_elo_hard": row["loser_hardelo"],
                    "away_elo_hard_games": row["loser_hardelo_games"],
                    "home_elo_clay": row["winner_clayelo"],
                    "home_elo_clay_games": row["winner_clayelo_games"],
                    "away_elo_clay": row["loser_clayelo"],
                    "away_elo_clay_games": row["loser_clayelo_games"],
                    "home_elo_grass": row["winner_grasselo"],
                    "home_elo_grass_games": row["winner_grasselo_games"],
                    "away_elo_grass": row["loser_grasselo"],
                    "away_elo_grass_games": row["loser_grasselo_games"],
                },
            )
