import logging
import time
import warnings
from datetime import timedelta

import numpy as np
from django.utils import timezone
from psycopg2.extensions import AsIs
from tabulate import tabulate
from tennisapi.models import Bet, BetWta, Match, Players, WtaMatch, WTAPlayers
from tennisapi.ml.utils import probability_of_winning
from .get_data import get_data

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def define_query_parameters(level, tour, from_at, end_at, surface, now):
    if level == "atp":
        bet_qs = Bet.objects.all()
        match_qs = Match.objects.all()
        player_qs = Players.objects.all()
        tour_table = "tennisapi_atptour"
        matches_table = "tennisapi_atpmatches"
        match_table = "tennisapi_match"
        player_table = "tennisapi_players"
        hard_elo = "tennisapi_atphardelo"
        grass_elo = "tennisapi_atpgrasselo"
        clay_elo = "tennisapi_atpclayelo"
        bet_table = "tennisapi_bet"
    else:
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
    date = "2015-1-1"
    params = {
        "tour_table": AsIs(tour_table),
        "matches_table": AsIs(matches_table),
        "player_table": AsIs(player_table),
        "match_table": AsIs(match_table),
        "hard_elo": AsIs(hard_elo),
        "grass_elo": AsIs(grass_elo),
        "clay_elo": AsIs(clay_elo),
        "start_at": from_at,
        "end_at": end_at,
        "surface": AsIs(surface),
        "query_surface": AsIs(surface),
        "bet_table": AsIs(bet_table),
        "event": AsIs(tour),
        "date": date,
        "event_id": None,
        "tourney_name": None,
    }
    log.info("Surface: %s", surface)
    return params, match_qs, bet_qs, player_qs, surface


def history_bet():
    now = timezone.now().date()
    surface_name = "clay"
    surface = AsIs(surface_name)
    level = "atp"
    tour = None
    from_at = "2024-1-1"
    end_at = now + timedelta(days=3)
    params, match_qs, bet_qs, player_qs, surface = define_query_parameters(
        level, tour, from_at, end_at, surface, now
    )
    data = get_data(params)
    # filetr by field winner_clayelo_games
    data = data[
        (data["winner_clayelo_games"] > 14)
        & (data["loser_clayelo_games"] > 14)
        & (data["winner_hardelo_games"] > 14)
        & (data["loser_hardelo_games"] > 14)
    ]
    columns = [
        "winner_fullname",
        "loser_fullname",
    ]
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"  # noqa E501
    )

    if len(data.index) == 0:
        print("No data")
        return

    if surface_name == "clay":
        elo_prob_field = "elo_prob_clay"
    elif surface_name == "grass":
        elo_prob_field = "elo_prob_grass"
    else:
        elo_prob_field = "elo_prob_hard"
    # Away player stats win

    data["date"] = data["start_at"].dt.strftime("%Y-%m-%d")

    data["home_odds"] = data["home_odds"].astype(float)
    data["away_odds"] = data["away_odds"].astype(float)

    data["elo_prob_hard"] = data["winner_hardelo"] - data["loser_hardelo"]
    data["elo_prob_hard"] = data["elo_prob_hard"].apply(probability_of_winning).round(2)  # noqa E501

    data["elo_prob_clay"] = data["winner_clayelo"] - data["loser_clayelo"]
    data["elo_prob_clay"] = data["elo_prob_clay"].apply(probability_of_winning).round(2)  # noqa E501

    data["elo_prob_grass"] = data["winner_grasselo"] - data["loser_grasselo"]
    data["elo_prob_grass"] = (
        data["elo_prob_grass"].apply(probability_of_winning).round(2)
    )
    bankroll = 2000
    bet_counter = 0
    total = 0
    data = data.replace(np.nan, None, regex=True)

    for index, row in data.iterrows():
        #time.sleep(0.1)
        """print(
            row["date"],
            row["winner_name"],
            row["loser_name"],
            row["home_id"],
            row["away_id"],
        )"""
        if bankroll <= 0.1:
            print("Bankroll is zero", bet_counter, total)
            break
        elo_prob = row[elo_prob_field] * 0.75 + row["elo_prob_hard"] * 0.25
        if elo_prob is None:
            continue
        if row["home_odds"] is None or row["away_odds"] is None:
            continue
        home_yield = row["home_odds"] * elo_prob
        away_yield = row["away_odds"] * (1 - elo_prob)
        winner_code = row["winner_code"]
        if home_yield > 1:
            bet_counter += 1
            bet_amount = (home_yield - 1) / (row["home_odds"] - 1) * bankroll
            if bet_amount > (bankroll * 0.05):
                bet_amount = bankroll * 0.05
            print(
                round(bet_amount, 0),
                round(bankroll, 0),
                row["away_odds"],
                row["home_odds"],
            )
            if winner_code == 1:
                bankroll += bet_amount * (row["home_odds"] - 1)
            elif winner_code == 2:
                bankroll -= bet_amount
            else:
                continue
        if away_yield > 1:
            bet_counter += 1
            bet_amount = (away_yield - 1) / (row["away_odds"] - 1) * bankroll
            if bet_amount > (bankroll * 0.05):
                bet_amount = bankroll * 0.05
            print(
                round(bet_amount, 0),
                round(bankroll, 0),
                row["away_odds"],
                row["home_odds"],
            )
            if winner_code == 2:
                bankroll += bet_amount * (row["away_odds"] - 1)
            elif winner_code == 1:
                bankroll -= bet_amount
            else:
                continue
        total += 1
    print(f"BetCounter: {bet_counter} Total: {total} Bankroll: {bankroll}")
