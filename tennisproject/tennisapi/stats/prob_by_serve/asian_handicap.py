import logging
from itertools import product

log = logging.getLogger(__name__)
# log.propagate = False


def asian_handicap(set_score_probs):
    # Calculate the game differences for each set score
    game_diffs = {
        score: int(score[0]) - int(score[1]) for score in set_score_probs.keys()
    }
    log.info("Game Score Differences for Each Set: %s", game_diffs)
    print("Game Score Differences for Each Set: %s", game_diffs)

    # Calculate the individual games won in each set score
    games_won = {
        score: int(score[0]) + int(score[1]) for score in set_score_probs.keys()
    }

    # Calculate the probability of each possible match outcome in terms of game score difference
    # Initialize a dictionary to hold cumulative probabilities of game differences
    cumulative_game_diff_probs = {}

    prob_over_215 = 0
    prob_over_225 = 0
    prob_over_235 = 0
    prob_over_245 = 0
    prob_over_255 = 0

    # Define a helper function to update the cumulative probabilities
    def update_cumulative_probs(game_diff, match_prob):
        if game_diff in cumulative_game_diff_probs:
            cumulative_game_diff_probs[game_diff] += match_prob
        else:
            cumulative_game_diff_probs[game_diff] = match_prob

    i = 0
    # Iterate over all possible pairs of sets, assuming the match ends as soon as a player wins two sets
    for set1, set2 in product(set_score_probs.keys(), repeat=2):
        total_games = games_won[set1] + games_won[set2]
        prob_two_sets = set_score_probs[set1] * set_score_probs[set2]

        # Compute the combined game difference and probability for the two sets
        game_diff_combined = game_diffs[set1] + game_diffs[set2]
        prob_combined = set_score_probs[set1] * set_score_probs[set2]

        # Handle the case where the home player wins both sets
        if (
            (set1[0] == "6" and set2[0] == "6")
            or (set1[0] == "7" and set2[0] == "6")
            or (set1[0] == "7" and set2[0] == "7")
            or (set1[0] == "6" and set2[0] == "7")
        ):
            update_cumulative_probs(game_diff_combined, prob_combined)
            # The match ends in two sets
            if total_games > 21.5:
                prob_over_215 += prob_two_sets
            if total_games > 22.5:
                prob_over_225 += prob_two_sets
            if total_games > 23.5:
                prob_over_235 += prob_two_sets
            if total_games > 24.5:
                prob_over_245 += prob_two_sets
            if total_games > 25.5:
                prob_over_255 += prob_two_sets
        # Handle the case where the opponent wins both sets
        elif (
            (set1[1] == "6" and set2[1] == "6")
            or (set1[1] == "7" and set2[1] == "6")
            or (set1[1] == "7" and set2[1] == "7")
            or (set1[1] == "6" and set2[1] == "7")
        ):
            update_cumulative_probs(game_diff_combined, prob_combined)
            # The match ends in two sets
            if total_games > 21.5:
                prob_over_215 += prob_two_sets
            if total_games > 22.5:
                prob_over_225 += prob_two_sets
            if total_games > 23.5:
                prob_over_235 += prob_two_sets
            if total_games > 24.5:
                prob_over_245 += prob_two_sets
            if total_games > 25.5:
                prob_over_255 += prob_two_sets
        # Handle the case where each player wins one of the sets (requires a third set to decide the match)
        else:
            for set3 in set_score_probs.keys():
                if (
                    (set1[0] == "6" and set3[0] == "6")
                    or (set2[0] == "6" and set3[0] == "6")
                    or (set1[0] == "7" and set3[0] == "6")
                    or (set2[0] == "7" and set3[0] == "6")
                    or (set1[0] == "7" and set3[0] == "7")
                    or (set2[0] == "7" and set3[0] == "7")
                    or (set1[0] == "6" and set3[0] == "7")
                    or (set2[0] == "6" and set3[0] == "7")
                ):
                    game_diff_final = game_diff_combined + game_diffs[set3]
                    prob_final = prob_combined * set_score_probs[set3]
                    update_cumulative_probs(game_diff_final, prob_final)

                    total_games_third_set = total_games + games_won[set3]
                    prob_three_sets = prob_two_sets * set_score_probs[set3]

                    # Update counters
                    if total_games_third_set > 21.5:
                        prob_over_215 += prob_three_sets
                    if total_games_third_set > 22.5:
                        prob_over_225 += prob_three_sets
                    if total_games_third_set > 23.5:
                        prob_over_235 += prob_three_sets
                    if total_games_third_set > 24.5:
                        prob_over_245 += prob_three_sets
                    if total_games_third_set > 25.5:
                        prob_over_255 += prob_three_sets

                elif (
                    (set1[1] == "6" and set3[1] == "6")
                    or (set2[1] == "6" and set3[1] == "6")
                    or (set1[1] == "7" and set3[1] == "6")
                    or (set2[1] == "7" and set3[1] == "6")
                    or (set1[1] == "7" and set3[1] == "7")
                    or (set2[1] == "7" and set3[1] == "7")
                    or (set1[1] == "6" and set3[1] == "7")
                    or (set2[1] == "6" and set3[1] == "7")
                ):
                    game_diff_final = game_diff_combined + game_diffs[set3]
                    prob_final = prob_combined * set_score_probs[set3]
                    update_cumulative_probs(game_diff_final, prob_final)

                    total_games_third_set = total_games + games_won[set3]
                    prob_three_sets = prob_two_sets * set_score_probs[set3]

                    # Update counters
                    if total_games_third_set > 21.5:
                        prob_over_215 += prob_three_sets
                    if total_games_third_set > 22.5:
                        prob_over_225 += prob_three_sets
                    if total_games_third_set > 23.5:
                        prob_over_235 += prob_three_sets
                    if total_games_third_set > 24.5:
                        prob_over_245 += prob_three_sets
                    if total_games_third_set > 25.5:
                        prob_over_255 += prob_three_sets

    # Now you can use cumulative_game_diff_probs to calculate probabilities for various handicaps.
    # For a +5.5 handicap, sum the probabilities of game_diffs ≥ -5
    home_plus_75_handicap_prob = sum(
        prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -7
    )
    home_plus_65_handicap_prob = sum(
        prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -6
    )
    home_plus_55_handicap_prob = sum(
        prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -5
    )
    home_plus_45_handicap_prob = sum(
        prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -4
    )
    home_plus_35_handicap_prob = sum(
        prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -3
    )
    home_plus_25_handicap_prob = sum(
        prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -2
    )

    log.info(
        f"Probability of the home player covering a +5.5 game handicap: {home_plus_55_handicap_prob}"
    )
    log.info(
        f"Probability of the home player covering a +4.5 game handicap: {home_plus_45_handicap_prob}"
    )
    log.info(
        f"Probability of the home player covering a +3.5 game handicap: {home_plus_35_handicap_prob}"
    )
    log.info(f"Probability of the games total going over 21.5: {prob_over_215}")
    log.info(f"Probability of the games total going over 22.5: {prob_over_225}")
    log.info(f"Probability of the games total going over 23.5: {prob_over_235}")

    return (
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
    )


def asian_handicap_prob_best_of_five(set_score_probs):
    # Calculate the game differences for each set score
    game_diffs = {score: int(score[0]) - int(score[1]) for score in set_score_probs.keys()}
    log.info("Game Score Differences for Each Set: %s", game_diffs)
    print("Game Score Differences for Each Set: %s", game_diffs)

    # Calculate the individual games won in each set score
    games_won = {score: int(score[0]) + int(score[1]) for score in set_score_probs.keys()}

    # Initialize a dictionary to hold cumulative probabilities of game differences
    cumulative_game_diff_probs = {}
    prob_over_215 = 0
    prob_over_225 = 0
    prob_over_235 = 0
    prob_over_245 = 0
    prob_over_255 = 0

    # Define a helper function to update the cumulative probabilities
    def update_cumulative_probs(game_diff, match_prob):
        if game_diff in cumulative_game_diff_probs:
            cumulative_game_diff_probs[game_diff] += match_prob
        else:
            cumulative_game_diff_probs[game_diff] = match_prob

    # Function to check if a set is won by a player
    def is_set_won(set_score, player):
        if player == 'home':
            return (set_score[0] == '6' and set_score[1] <= '4') or (set_score[0] == '7' and set_score[1] <= '5')
        else:
            return (set_score[1] == '6' and set_score[0] <= '4') or (set_score[1] == '7' and set_score[0] <= '5')

    # Iterate over possible combinations of 5 sets won by either player
    for sets in product(set_score_probs.keys(), repeat=5):
        won_by_home = sum(is_set_won(set, 'home') for set in sets)
        won_by_away = sum(is_set_won(set, 'away') for set in sets)

        if won_by_home == 3 or won_by_away == 3:
            total_games = sum(games_won[set] for set in sets[:3])
            prob_three_sets = set_score_probs[sets[0]] * set_score_probs[sets[1]] * set_score_probs[sets[2]]

            game_diff_combined = game_diffs[sets[0]] + game_diffs[sets[1]] + game_diffs[sets[2]]

            update_cumulative_probs(game_diff_combined, prob_three_sets)

            if total_games > 21.5: prob_over_215 += prob_three_sets
            if total_games > 22.5: prob_over_225 += prob_three_sets
            if total_games > 23.5: prob_over_235 += prob_three_sets
            if total_games > 24.5: prob_over_245 += prob_three_sets
            if total_games > 25.5: prob_over_255 += prob_three_sets

            for set4, set5 in product(set_score_probs.keys(), repeat=2):
                won_by_home = sum(is_set_won(set, 'home') for set in [sets[0], sets[1], sets[2], set4, set5])
                won_by_away = sum(is_set_won(set, 'away') for set in [sets[0], sets[1], sets[2], set4, set5])

                if won_by_home == 3 or won_by_away == 3:
                    total_games_4 = total_games + games_won[set4]
                    prob_four_sets = prob_three_sets * set_score_probs[set4]

                    game_diff_combined_4 = game_diff_combined + game_diffs[set4]

                    update_cumulative_probs(game_diff_combined_4, prob_four_sets)

                    if total_games_4 > 21.5: prob_over_215 += prob_four_sets
                    if total_games_4 > 22.5: prob_over_225 += prob_four_sets
                    if total_games_4 > 23.5: prob_over_235 += prob_four_sets
                    if total_games_4 > 24.5: prob_over_245 += prob_four_sets
                    if total_games_4 > 25.5: prob_over_255 += prob_four_sets

                    total_games_5 = total_games_4 + games_won[set5]
                    prob_five_sets = prob_four_sets * set_score_probs[set5]

                    game_diff_combined_5 = game_diff_combined_4 + game_diffs[set5]

                    update_cumulative_probs(game_diff_combined_5, prob_five_sets)

                    if total_games_5 > 21.5: prob_over_215 += prob_five_sets
                    if total_games_5 > 22.5: prob_over_225 += prob_five_sets
                    if total_games_5 > 23.5: prob_over_235 += prob_five_sets
                    if total_games_5 > 24.5: prob_over_245 += prob_five_sets
                    if total_games_5 > 25.5: prob_over_255 += prob_five_sets

    # Calculate probabilities for various handicaps
    home_plus_75_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -7)
    home_plus_65_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -6)
    home_plus_55_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -5)
    home_plus_45_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -4)
    home_plus_35_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -3)
    home_plus_25_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -2)

    log.info(f"Probability of the home player covering a +7.5 game handicap: {home_plus_75_handicap_prob}")
    log.info(f"Probability of the home player covering a +6.5 game handicap: {home_plus_65_handicap_prob}")
    log.info(f"Probability of the home player covering a +5.5 game handicap: {home_plus_55_handicap_prob}")
    log.info(f"Probability of the home player covering a +4.5 game handicap: {home_plus_45_handicap_prob}")
    log.info(f"Probability of the home player covering a +3.5 game handicap: {home_plus_35_handicap_prob}")
    log.info(f"Probability of the games total going over 21.5: {prob_over_215}")
    log.info(f"Probability of the games total going over 22.5: {prob_over_225}")
    log.info(f"Probability of the games total going over 23.5: {prob_over_235}")

    return (
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
        prob_over_255
    )
