import scipy.stats as sps
import numpy as np
from vakio.models import MonivetoProb
from numpy import random


def calculate_poisson(
        average_goals_team_a,
        average_goals_team_b,
        match_nro,
        moniveto_id,
        list_index,
):
    print(f"Team A: {average_goals_team_a} Team B: {average_goals_team_b}")
    max_goals = 9

    # Calculate base Poisson PMF
    poisson_team_a = sps.poisson.pmf(np.arange(max_goals + 1), average_goals_team_a)
    poisson_team_b = sps.poisson.pmf(np.arange(max_goals + 1), average_goals_team_b)

    prob_matrix = np.zeros((max_goals + 1, max_goals + 1))
    empty_net_factor = 1.15
    trailing_team_factor = 1.1

    total_prob = 0
    prob_home_win, prob_draw, prob_away_win = 0, 0, 0
    under_4_5, under_5_5, under_2_5 = 0, 0, 0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            base_prob = poisson_team_a[i] * poisson_team_b[j]
            adjusted_prob = base_prob

            # Adjust probabilities based on game situation
            if i > j:
                goal_diff = i - j
                if goal_diff == 1:
                    # Close game
                    if j >= i-1 and i >= 2:
                        adjusted_prob *= empty_net_factor
                elif goal_diff == 2:
                    adjusted_prob *= trailing_team_factor
            elif j > i:
                goal_diff = j - i
                if goal_diff == 1:
                    if i >= j-1 and j >= 2:
                        adjusted_prob *= empty_net_factor
                elif goal_diff == 2:
                    adjusted_prob *= trailing_team_factor
            elif i == j:
                # Adjust draw probabilities for regular time
                # Draws are more common in regular time
                if i <= 3:  # 0-0, 1-1, 2-2, 3-3 are common draws
                    adjusted_prob *= 1.3
                else:  # Higher scoring draws are less common
                    adjusted_prob *= 1.1

            prob_matrix[i, j] = adjusted_prob
            total_prob += adjusted_prob

            if i + j < 6:
                under_5_5 += adjusted_prob
            if i + j < 5:
                under_4_5 += adjusted_prob
            if i + j < 3:
                under_2_5 += adjusted_prob

    # Normalize probabilities
    prob_matrix = prob_matrix / total_prob

    # Calculate final probabilities
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            normalized_prob = prob_matrix[i, j]

            MonivetoProb.objects.update_or_create(
                combination=f"{match_nro}-{i}-{j}",
                moniveto_id=moniveto_id,
                list_index=list_index,
                defaults={
                    "match_nro": match_nro,
                    "score": f"{i}-{j}",
                    "prob": normalized_prob
                }
            )

            if i > j:
                prob_home_win += normalized_prob
            elif i < j:
                prob_away_win += normalized_prob
            else:
                prob_draw += normalized_prob

    # Normalize under/over probabilities
    under_5_5 /= total_prob
    under_4_5 /= total_prob
    under_2_5 /= total_prob

    print(f"Probability of home win: {prob_home_win:.3f} ({1/prob_home_win:.2f})")
    print(f"Probability of draw: {prob_draw:.3f} ({1/prob_draw:.2f})")
    print(f"Probability of away win: {prob_away_win:.3f} ({1/prob_away_win:.2f})")
    print(f"Sum of probabilities: {prob_home_win + prob_draw + prob_away_win:.3f}")
    print(f"Under 4.5: {under_4_5:.3f} ({1/under_4_5:.2f}) Over 4.5: {1-under_4_5:.3f} ({1/(1-under_4_5):.2f})")
    print(f"Under 5.5: {under_5_5:.3f} ({1/under_5_5:.2f}) Over 5.5: {1-under_5_5:.3f} ({1/(1-under_5_5):.2f})")
    print(f"Under 2.5: {under_2_5:.3f} ({1/under_2_5:.2f}) Over 2.5: {1-under_2_5:.3f} ({1/(1-under_2_5):.2f})")

def dixon_coles_correction(home_goals, away_goals, home_rate, away_rate, rho):
    if home_goals == 0 and away_goals == 0:
        return 1 - rho
    elif home_goals == 1 and away_goals == 0:
        return 1 + rho
    elif home_goals == 0 and away_goals == 1:
        return 1 + rho
    elif home_goals == 1 and away_goals == 1:
        return 1 - rho
    else:
        return 1.0

def adjusted_probability(home_goals, away_goals, home_rate, away_rate, rho=-0.1):
    # Calculate basic Poisson probabilities
    home_prob = np.exp(-home_rate) * (home_rate ** home_goals) / np.math.factorial(home_goals)
    away_prob = np.exp(-away_rate) * (away_rate ** away_goals) / np.math.factorial(away_goals)

    # Apply Dixon-Coles correction
    correction = dixon_coles_correction(home_goals, away_goals, home_rate, away_rate, rho)

    return home_prob * away_prob * correction

def calculate_poisson_football(
        average_goals_team_a,
        average_goals_team_b,
        match_nro,
        moniveto_id,
        list_index,
):
    max_goals = 9
    prob_home_win, prob_draw, prob_away_win = 0, 0, 0
    under_4_5, under_5_5, under_2_5 = 0, 0, 0
    # Calculate joint probabilities for all match outcomes
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            total_goals = i + j
            prob = adjusted_probability(i, j, average_goals_team_a, average_goals_team_b)
            #print(f"Probability of {i}-{j}: {prob:.6f}")
            if total_goals < 6:
                under_5_5 += prob
            if total_goals < 5:
                under_4_5 += prob
            if total_goals < 3:
                under_2_5 += prob
            match_prob = prob
            #print(f"Probability of {i}-{j} score: {match_prob:.3f} odds: {1/match_prob:.3f}")
            MonivetoProb.objects.update_or_create(
                combination=f"{match_nro}-{i}-{j}",
                moniveto_id=moniveto_id,
                list_index=list_index,
                defaults={
                    "match_nro": match_nro,
                    "score": f"{i}-{j}",
                    "prob": match_prob#*0.95,
                }
            )

            # Check the match outcome
            if i > j:
                prob_home_win += match_prob
            elif i < j:
                prob_away_win += match_prob
            else:
                prob_draw += match_prob

    print(f"Probability of home win: {prob_home_win:.2f} / {1/prob_home_win:.2f}")
    print(f"Probability of draw: {prob_draw:.2f} / {1/prob_draw:.2f}")
    print(f"Probability of away win: {prob_away_win:.2f} / {1/prob_away_win:.2f}")
    print(f"Probability of 4.5 goals: {(1-under_4_5):.2f} / {1/(1-under_4_5):.2f} / {under_4_5:.2f} / {1/under_4_5:.2f}")
    print(f"Probability of 5.5 goals: {(1-under_5_5):.2f} / {1/(1-under_5_5):.2f} /{under_5_5:.2f} / {1/under_5_5:.2f}")
    print(f"Probability of 2.5 goals: {(1-under_2_5):.2f} / {1/(1-under_2_5):.2f} / {under_2_5:.2f} / {1/under_2_5:.2f}")
