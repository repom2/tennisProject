## calculates probability of winning a tennis match from any given score dependent on the skill levels
## of the two players

import logging
import math

import pandas as pd
from tennisapi.stats.prob_by_serve.asian_handicap import (
    asian_handicap,
    asian_handicap_prob_best_of_five,
)
from tennisapi.stats.prob_by_serve.game_prob import gameProb
from tennisapi.stats.prob_by_serve.tiebreak_prob import tiebreakProb
from tennisapi.stats.prob_by_serve.winning_set import setGeneral

log = logging.getLogger(__name__)
# log.propagate = False


def binomial_probability(n, k, p):
    # Calculate binomial probability
    c = math.comb(n, k)  # Number of combinations (n choose k)
    return c * p**k * (1 - p) ** (n - k)


def fact(x):
    if x in [0, 1]:
        return 1
    r = 1
    for a in range(1, (x + 1)):
        r = r * a
    return r


def ch(a, b):
    return fact(a) / (fact(b) * fact(a - b))


def matchGeneral(e, v=0, w=0, s=3):
    ## calculates probability of winning the match
    ## from the beginning of a set
    ## e is p(winning a set)
    ## v and w is current set score
    ## s is total number of sets ("best of")
    towin = (s + 1) / 2
    left = int(towin - v)
    if left == 0:
        return 1
    remain = int(s - v - w)
    if left > remain:
        return 0
    win = 0
    for i in range(left, (remain + 1)):
        add = (
            ch((i - 1), (left - 1))
            * (e[0] ** (left - 1))
            * ((1 - e[0]) ** (i - left))
            * e[0]
        )
        win += add
    return win


# Original
def matchProb(s, t, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3):
    ## calculates probability of winning a match from any given score,
    ## given:
    ## s, t: p(server wins a service point), p(server wins return point)
    ## gv, gw: current score within the game. e.g. 30-15 is 2, 1
    ## sv, sw: current score within the set. e.g. 5, 4
    ## mv, mw: current score within the match (number of sets for each player)
    ## v's are serving player; w's are returning player
    ## sets: "best of", so default is best of 3

    a = gameProb(s)
    # log.info("probability of server winning a single game: %s", a)

    b = gameProb(t)
    wins_single_game = b
    # log.info("probability of returner winning a single game: %s", b)

    c = setGeneral(s, t)
    wins_single_set = c[0]
    # log.info("probability of server winning a single set: %s", c)

    if gv == 0 and gw == 0:  ## no point score
        if sv == 0 and sw == 0:  ## no game score
            stats_win = matchGeneral(c, v=mv, w=mw, s=sets)
            return stats_win
        else:  ## we're in mid-set, no point score
            sWin = setGeneral(a, b, s, t, v=sv, w=sw)
            sLoss = 1 - sWin
    elif sv == 6 and sw == 6:
        sWin = tiebreakProb(s, t, v=gv, w=gw)
        sLoss = 1 - sWin
    else:
        gWin = gameProb(s, v=gv, w=gw)
        gLoss = 1 - gWin
        sWin = gWin * (
            1 - setGeneral((1 - b), (1 - a), (1 - t), (1 - s), v=sw, w=(sv + 1))
        )
        sWin += gLoss * (
            1 - setGeneral((1 - b), (1 - a), (1 - t), (1 - s), v=(sw + 1), w=sv)
        )
        sLoss = 1 - sWin
    mWin = sWin * matchGeneral(c, v=(mv + 1), w=mw, s=sets)
    mWin += sLoss * matchGeneral(c, v=mv, w=(mw + 1), s=sets)
    return mWin


def match_prob(home_spw, away_spw, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3):
    ## calculates probability of winning a match from any given score,
    ## given:
    ## s, t: p(server wins a service point), p(server wins return point)
    ## gv, gw: current score within the game. e.g. 30-15 is 2, 1
    ## sv, sw: current score within the set. e.g. 5, 4
    ## mv, mw: current score within the match (number of sets for each player)
    ## v's are serving player; w's are returning player
    ## sets: "best of", so default is best of 3

    # Get away handicaps by calling the function with reversed parameters
    away_probs = match_prob_internal(
        away_spw, 1 - home_spw, gw, gv, sw, sv, mw, mv, sets
    )

    # Call the main function for home probabilities
    home_probs = match_prob_internal(
        home_spw, 1 - away_spw, gv, gw, sv, sw, mv, mw, sets
    )

    # Create a combined result with both home and away handicaps
    result = pd.Series(
        {
            "stats_win": home_probs["stats_win"],
            "home_wins_single_game": home_probs["home_wins_single_game"],
            "home_wins_single_set": home_probs["home_wins_single_set"],
            "home_wins_1_set": home_probs["home_wins_1_set"],
            "home_wins_2_set": home_probs["home_wins_2_set"],
            "home_ah_7_5": home_probs["home_ah_7_5"],
            "home_ah_6_5": home_probs["home_ah_6_5"],
            "home_ah_5_5": home_probs["home_ah_5_5"],
            "home_ah_4_5": home_probs["home_ah_4_5"],
            "home_ah_3_5": home_probs["home_ah_3_5"],
            "home_ah_2_5": home_probs["home_ah_2_5"],
            "away_ah_7_5": away_probs["home_ah_7_5"],
            "away_ah_6_5": away_probs["home_ah_6_5"],
            "away_ah_5_5": away_probs["home_ah_5_5"],
            "away_ah_4_5": away_probs["home_ah_4_5"],
            "away_ah_3_5": away_probs["home_ah_3_5"],
            "away_ah_2_5": away_probs["home_ah_2_5"],
            "games_over_21_5": home_probs["games_over_21_5"],
            "games_over_22_5": home_probs["games_over_22_5"],
            "games_over_23_5": home_probs["games_over_23_5"],
            "games_over_24_5": home_probs["games_over_24_5"],
            "games_over_25_5": home_probs["games_over_25_5"],
        }
    )

    return result


def match_prob_internal(s, t, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3):
    ## calculates probability of winning a match from any given score,
    ## given:
    ## s, t: p(server wins a service point), p(server wins return point)
    ## gv, gw: current score within the game. e.g. 30-15 is 2, 1
    ## sv, sw: current score within the set. e.g. 5, 4
    ## mv, mw: current score within the match (number of sets for each player)
    ## v's are serving player; w's are returning player
    ## sets: "best of", so default is best of 3

    index_columns = [
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

    a = gameProb(s)
    # log.info("probability of server winning a single game: %s", a)

    b = gameProb(t)
    wins_single_game = b
    # log.info("probability of returner winning a single game: %s", b)

    c = setGeneral(s, t)
    wins_single_set = c[0]
    # log.info("probability of server winning a single set: %s", c)

    # probability to win one set in best of 3
    if sets == 3:
        if c[0] > 0.5:
            win_set = 1 - c[0]
        else:
            win_set = c[0]
        server_2_0 = win_set**2
        server_2_1 = 2 * win_set**2 * (1 - win_set)
        server_1_2 = 2 * win_set * (1 - win_set) ** 2
        server_0_2 = (1 - win_set) ** 2
        wins_1_set = server_1_2 + server_2_0 + server_2_1
        wins_2_set = None
        (
            home_plus_75_handicap_prob,
            home_plus_65_handicap_prob,
            home_plus_55_handicap_prob,
            home_plus_45_handicap_prob,
            home_plus_35_handicap_prob,
            home_plus_25_handicap_prob,
            prob_over_215,
            prob_over_225,
            prob_over_235,
            prob_over_245,
            prob_over_255,
        ) = asian_handicap(c[1])

    elif sets == 5:
        if c[0] > 0.5:
            win_set = 1 - c[0]
        else:
            win_set = c[0]
        p_3_0 = win_set**3
        p_3_1 = win_set**3 * (1 - win_set) * 3
        p_3_2 = win_set**3 * (1 - win_set) ** 2 * 6
        p_0_3 = (1 - win_set) ** 3
        p_1_3 = (1 - win_set) ** 3 * win_set * 3
        p_2_3 = (1 - win_set) ** 3 * win_set**2 * 6
        wins_1_set = p_1_3 + p_2_3 + p_3_0 + p_3_1 + p_3_2
        wins_2_set = p_2_3 + p_3_0 + p_3_1 + p_3_2
        (
            home_plus_75_handicap_prob,
            home_plus_65_handicap_prob,
            home_plus_55_handicap_prob,
            home_plus_45_handicap_prob,
            home_plus_35_handicap_prob,
            home_plus_25_handicap_prob,
            prob_over_215,
            prob_over_225,
            prob_over_235,
            prob_over_245,
            prob_over_255,
        ) = asian_handicap(c[1])

    if gv == 0 and gw == 0:  ## no point score
        if sv == 0 and sw == 0:  ## no game score
            stats_win = matchGeneral(c, v=mv, w=mw, s=sets)
            return pd.Series(
                [
                    stats_win,
                    wins_single_game,
                    wins_single_set,
                    wins_1_set,
                    wins_2_set,
                    home_plus_75_handicap_prob,
                    home_plus_65_handicap_prob,
                    home_plus_55_handicap_prob,
                    home_plus_45_handicap_prob,
                    home_plus_35_handicap_prob,
                    home_plus_25_handicap_prob,
                    prob_over_215,
                    prob_over_225,
                    prob_over_235,
                    prob_over_245,
                    prob_over_255,
                ],
                index=index_columns,
            )
        else:  ## we're in mid-set, no point score
            sWin = setGeneral(a, b, s, t, v=sv, w=sw)
            sLoss = 1 - sWin
    elif sv == 6 and sw == 6:
        sWin = tiebreakProb(s, t, v=gv, w=gw)
        sLoss = 1 - sWin
    else:
        gWin = gameProb(s, v=gv, w=gw)
        gLoss = 1 - gWin
        sWin = gWin * (
            1 - setGeneral((1 - b), (1 - a), (1 - t), (1 - s), v=sw, w=(sv + 1))
        )
        sWin += gLoss * (
            1 - setGeneral((1 - b), (1 - a), (1 - t), (1 - s), v=(sw + 1), w=sv)
        )
        sLoss = 1 - sWin
    mWin = sWin * matchGeneral(c, v=(mv + 1), w=mw, s=sets)
    mWin += sLoss * matchGeneral(c, v=mv, w=(mw + 1), s=sets)
    return pd.Series(
        [
            mWin,
            wins_single_game,
            wins_single_set,
            wins_1_set,
            wins_2_set,
            home_plus_75_handicap_prob,
            home_plus_65_handicap_prob,
            home_plus_55_handicap_prob,
            home_plus_45_handicap_prob,
            home_plus_35_handicap_prob,
            home_plus_25_handicap_prob,
            prob_over_215,
            prob_over_225,
            prob_over_235,
            prob_over_245,
            prob_over_255,
        ],
        index=index_columns,
    )
