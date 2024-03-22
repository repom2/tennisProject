import numpy as np
import scipy.stats as sps
from scipy.optimize import minimize

max_goals = 10  # Maximum number of goals to consider per team


def objective_func(goals_avg, desired_probabilities):
    average_goals_teamA, average_goals_teamB = goals_avg
    # print("Average goals for team A: {:.2f}".format(average_goals_teamA))

    # Calculate Poisson PMF for each team up to max goals
    poisson_teamA = sps.poisson.pmf(np.arange(max_goals+1), average_goals_teamA)
    poisson_teamB = sps.poisson.pmf(np.arange(max_goals+1), average_goals_teamB)
    prob_home_win, prob_draw, prob_away_win = 0, 0, 0

    # Calculate joint probabilities for all match outcomes
    for i in range(0, max_goals+1):
        for j in range(0, max_goals+1):
            match_prob = poisson_teamA[i] * poisson_teamB[j]

            # Check the match outcome
            if i > j:
                prob_home_win += match_prob
            elif i < j:
                prob_away_win += match_prob
            else:
                prob_draw += match_prob
    current_probabilities = np.array([prob_home_win, prob_draw, prob_away_win])
    return np.sum(np.square(desired_probabilities-current_probabilities))


def match_probability(
        odds_home_win,
        odds_draw,
        odds_away_win,
):
    desired_prob_home_win =  odds_home_win
    desired_prob_draw =  odds_draw
    desired_prob_away_win =  odds_away_win

    # Initial guess
    x0 = np.array([1.5, 1.3])
    print("Initial guess: {}".format(x0))

    desired_probabilities = np.array([
        desired_prob_home_win,
        desired_prob_draw,
        desired_prob_away_win
    ])

    # Optimization
    result = minimize(
        objective_func,
        x0,
        args=(desired_probabilities),
        method='Nelder-Mead'
    )
    estimated_avg_goals = result.x
    #print("Average goals for team A: {:.2f}".format(estimated_avg_goals[0]))
    #print("Average goals for team B: {:.2f}".format(estimated_avg_goals[1]))

    return estimated_avg_goals
