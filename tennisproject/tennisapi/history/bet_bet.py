import logging
import time
import warnings
from datetime import timedelta

import numpy as np
from django.utils import timezone
from psycopg2.extensions import AsIs
from tabulate import tabulate
from tennisapi.models import Bet, BetWta, Match, Players, WtaMatch, WTAPlayers, AtpMatches, WtaMatches
from tennisapi.ml.utils import probability_of_winning
from .get_data import get_data

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def bet_bet():
    level = "atp"
    surface = "hard"
    if level == "atp":
        data = Bet.objects.filter(
            surface=surface
        )
    else:
        data = BetWta.objects.filter(
            surface=surface
        )

    bankroll = 2000
    bet_counter = 0
    total = 0

    for row in data:
        #time.sleep(0.1)
        print(row.start_at, row.stats_win, row.home_odds, row.away_odds, row.home_prob, row.away_prob, row.home_elo_clay_games)
        if surface == "clay":
            if row.home_elo_clay_games == None or row.away_elo_clay_games == None or row.home_elo_clay_games < 6 or row.away_elo_clay_games < 6:
                continue
        if surface == "hard":
            if row.home_elo_hard_games == None or row.away_elo_hard_games == None or row.home_elo_hard_games < 6 or row.away_elo_hard_games < 6:
                continue
        if bankroll <= 0.1:
            print("Bankroll is zero", bet_counter, total)
            break
        #elo_prob = row.home_prob
        #elo_prob = row.stats_win
        elo_prob = row.stats_win_hard
        if elo_prob is None:
            continue
        if row.home_odds is None or row.away_odds is None:
            continue
        home_yield = row.home_odds * elo_prob
        away_yield = row.away_odds * (1 - elo_prob)
        if level == "atp":
            winner_code = (
                Match.objects.filter(
                    id=row.match_id
                )
                .exclude(round_name__icontains="qualif")
                #.exclude(round_name__icontains="r")
                .values_list("winner_code", flat=True).first()
            )
        else:
            winner_code = (
                WtaMatch.objects.filter(
                    id=row.match_id
                )
                .exclude(round_name__icontains="qualif")
                #.exclude(round_name__icontains="r")
                .values_list("winner_code", flat=True).first()
            )
        if winner_code is None:
            continue
        print("Winner code", winner_code)
        if home_yield > 1:
            bet_counter += 1
            bet_amount = (home_yield - 1) / (row.home_odds - 1) * bankroll
            if bet_amount > (bankroll * 0.05):
                bet_amount = bankroll * 0.05
            print(
                round(bet_amount, 0),
                round(bankroll, 0),
                row.away_odds,
                row.home_odds,
            )
            if winner_code == 1:
                bankroll += bet_amount * (row.home_odds - 1)
            elif winner_code == 2:
                bankroll -= bet_amount
            else:
                continue
        if away_yield > 1:
            bet_counter += 1
            bet_amount = (away_yield - 1) / (row.away_odds - 1) * bankroll
            if bet_amount > (bankroll * 0.05):
                bet_amount = bankroll * 0.05
            print(
                round(bet_amount, 0),
                round(bankroll, 0),
                row.away_odds,
                row.home_odds,
            )
            if winner_code == 2:
                bankroll += bet_amount * (row.away_odds - 1)
            elif winner_code == 1:
                bankroll -= bet_amount
            else:
                continue
        total += 1
    print(f"BetCounter: {bet_counter} Total: {total} Bankroll: {bankroll}")
