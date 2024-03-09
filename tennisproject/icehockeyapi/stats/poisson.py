import scipy.stats as sps
import numpy as np
from numpy import random


def calculate_poisson(
        average_goals_team_a,
        average_goals_team_b,
):
    # All possible number of goals scored
    max_goals = 9

    # Calculate Poisson PMF for each team up to max goals
    poisson_team_a = sps.poisson.pmf(np.arange(max_goals + 1), average_goals_team_a)
    poisson_team_b = sps.poisson.pmf(np.arange(max_goals + 1), average_goals_team_b)

    prob_home_win, prob_draw, prob_away_win = 0, 0, 0

    # Calculate joint probabilities for all match outcomes
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            match_prob = poisson_team_a[i] * poisson_team_b[j]
            # Check the match outcome
            if i > j:
                prob_home_win += match_prob
            elif i < j:
                prob_away_win += match_prob
            else:
                prob_draw += match_prob

    return round(prob_home_win, 2), round(prob_draw, 2), round(prob_away_win,2)
