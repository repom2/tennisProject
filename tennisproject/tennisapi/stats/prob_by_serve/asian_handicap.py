import logging
from itertools import product

log = logging.getLogger(__name__)
# log.propagate = False


def _is_set_won(set_score_str, player):
    """
    Determines if the player won the set based on the score string.
    Example: set_score_str="64", player="home" -> True
             set_score_str="57", player="home" -> False
             set_score_str="76", player="home" -> True
    """
    try:
        p_score = int(set_score_str[0])
        o_score = int(set_score_str[1])
    except (ValueError, IndexError):
        # Handle cases like "76" where direct indexing might be tricky if not careful
        # However, standard scores like "60", "75" are expected.
        # Assuming scores are single digits for games like "6-0", "7-5".
        # This simple parsing works for "XY" format.
        # If scores can be "10-8" (not typical in tennis sets), parsing needs adjustment.
        # For "76", p_score=7, o_score=6.
        # For "67", p_score=6, o_score=7.
        # This parsing is okay for typical tennis set scores.
        pass


    if player == "home":
        if p_score == 6 and o_score <= 4: return True
        if p_score == 7 and (o_score == 5 or o_score == 6): return True
    elif player == "away":
        if o_score == 6 and p_score <= 4: return True
        if o_score == 7 and (p_score == 5 or p_score == 6): return True
    return False


def asian_handicap(set_score_probs):
    # Calculate the game differences for each set score
    game_diffs = {
        score: int(score[0]) - int(score[1]) for score in set_score_probs.keys()
    }
    # Calculate the individual games won in each set score
    games_total_map = {
        score: int(score[0]) + int(score[1]) for score in set_score_probs.keys()
    }

    cumulative_game_diff_probs = {}
    prob_over_215 = 0
    prob_over_225 = 0
    prob_over_235 = 0
    prob_over_245 = 0
    prob_over_255 = 0

    def update_cumulative_probs(game_diff, match_prob):
        cumulative_game_diff_probs[game_diff] = cumulative_game_diff_probs.get(game_diff, 0) + match_prob

    all_set_scores = list(set_score_probs.keys())

    # Iterate over possible outcomes for a best-of-3 match
    for s1, s2 in product(all_set_scores, repeat=2):
        prob_s1 = set_score_probs[s1]
        prob_s2 = set_score_probs[s2]

        # Home wins 2-0
        if _is_set_won(s1, 'home') and _is_set_won(s2, 'home'):
            match_prob = prob_s1 * prob_s2
            current_game_diff = game_diffs[s1] + game_diffs[s2]
            total_games = games_total_map[s1] + games_total_map[s2]
            update_cumulative_probs(current_game_diff, match_prob)

            if total_games > 21.5: prob_over_215 += match_prob
            if total_games > 22.5: prob_over_225 += match_prob
            if total_games > 23.5: prob_over_235 += match_prob
            if total_games > 24.5: prob_over_245 += match_prob
            if total_games > 25.5: prob_over_255 += match_prob
        
        # Away wins 2-0
        elif _is_set_won(s1, 'away') and _is_set_won(s2, 'away'):
            match_prob = prob_s1 * prob_s2
            current_game_diff = game_diffs[s1] + game_diffs[s2] # from home's perspective
            total_games = games_total_map[s1] + games_total_map[s2]
            update_cumulative_probs(current_game_diff, match_prob)

            if total_games > 21.5: prob_over_215 += match_prob
            if total_games > 22.5: prob_over_225 += match_prob
            if total_games > 23.5: prob_over_235 += match_prob
            if total_games > 24.5: prob_over_245 += match_prob
            if total_games > 25.5: prob_over_255 += match_prob

        # Match goes to 3 sets
        else:
            for s3 in all_set_scores:
                prob_s3 = set_score_probs[s3]
                match_prob_3sets = prob_s1 * prob_s2 * prob_s3
                
                # Home wins 2-1
                if (_is_set_won(s1, 'home') and _is_set_won(s2, 'away') and _is_set_won(s3, 'home')) or \
                   (_is_set_won(s1, 'away') and _is_set_won(s2, 'home') and _is_set_won(s3, 'home')):
                    current_game_diff = game_diffs[s1] + game_diffs[s2] + game_diffs[s3]
                    total_games = games_total_map[s1] + games_total_map[s2] + games_total_map[s3]
                    update_cumulative_probs(current_game_diff, match_prob_3sets)

                    if total_games > 21.5: prob_over_215 += match_prob_3sets
                    if total_games > 22.5: prob_over_225 += match_prob_3sets
                    if total_games > 23.5: prob_over_235 += match_prob_3sets
                    if total_games > 24.5: prob_over_245 += match_prob_3sets
                    if total_games > 25.5: prob_over_255 += match_prob_3sets

                # Away wins 2-1 (Home loses 1-2)
                elif (_is_set_won(s1, 'home') and _is_set_won(s2, 'away') and _is_set_won(s3, 'away')) or \
                     (_is_set_won(s1, 'away') and _is_set_won(s2, 'home') and _is_set_won(s3, 'away')):
                    current_game_diff = game_diffs[s1] + game_diffs[s2] + game_diffs[s3]
                    total_games = games_total_map[s1] + games_total_map[s2] + games_total_map[s3]
                    update_cumulative_probs(current_game_diff, match_prob_3sets)

                    if total_games > 21.5: prob_over_215 += match_prob_3sets
                    if total_games > 22.5: prob_over_225 += match_prob_3sets
                    if total_games > 23.5: prob_over_235 += match_prob_3sets
                    if total_games > 24.5: prob_over_245 += match_prob_3sets
                    if total_games > 25.5: prob_over_255 += match_prob_3sets
    
    home_plus_75_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -7)
    home_plus_65_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -6)
    home_plus_55_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -5)
    home_plus_45_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -4)
    home_plus_35_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -3)
    home_plus_25_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -2)

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
    game_diffs = {
        score: int(score[0]) - int(score[1]) for score in set_score_probs.keys()
    }
    games_total_map = {
        score: int(score[0]) + int(score[1]) for score in set_score_probs.keys()
    }

    cumulative_game_diff_probs = {}
    prob_over_215 = 0
    prob_over_225 = 0
    prob_over_235 = 0
    prob_over_245 = 0
    prob_over_255 = 0 # Should add more for 5-set matches, e.g., up to 30.5, 32.5 etc.

    def update_accumulators(current_game_diff, total_games, match_prob):
        nonlocal prob_over_215, prob_over_225, prob_over_235, prob_over_245, prob_over_255
        cumulative_game_diff_probs[current_game_diff] = cumulative_game_diff_probs.get(current_game_diff, 0) + match_prob
        if total_games > 21.5: prob_over_215 += match_prob
        if total_games > 22.5: prob_over_225 += match_prob
        if total_games > 23.5: prob_over_235 += match_prob
        if total_games > 24.5: prob_over_245 += match_prob
        if total_games > 25.5: prob_over_255 += match_prob
        # Add more "over" checks if needed for 5-set matches
        # e.g., if total_games > 26.5: prob_over_265 += match_prob ...

    all_set_scores = list(set_score_probs.keys())

    # 3-Set Matches (Home 3-0 or Away 3-0)
    for s1, s2, s3 in product(all_set_scores, repeat=3):
        prob = set_score_probs[s1] * set_score_probs[s2] * set_score_probs[s3]
        current_total_games = games_total_map[s1] + games_total_map[s2] + games_total_map[s3]
        current_game_diff = game_diffs[s1] + game_diffs[s2] + game_diffs[s3]

        h_wins = sum(_is_set_won(s, 'home') for s in [s1, s2, s3])
        a_wins = sum(_is_set_won(s, 'away') for s in [s1, s2, s3])

        if h_wins == 3 and a_wins == 0: # Home wins 3-0
            update_accumulators(current_game_diff, current_total_games, prob)
        elif a_wins == 3 and h_wins == 0: # Away wins 3-0
            update_accumulators(current_game_diff, current_total_games, prob)

    # 4-Set Matches (Home 3-1 or Away 3-1)
    for s1, s2, s3, s4 in product(all_set_scores, repeat=4):
        prob = set_score_probs[s1] * set_score_probs[s2] * set_score_probs[s3] * set_score_probs[s4]
        current_total_games = games_total_map[s1] + games_total_map[s2] + games_total_map[s3] + games_total_map[s4]
        current_game_diff = game_diffs[s1] + game_diffs[s2] + game_diffs[s3] + game_diffs[s4]

        # Check for Home 3-1
        # Home must win s4, and 2 of (s1,s2,s3), Away must win 1 of (s1,s2,s3)
        if _is_set_won(s4, 'home'):
            h_first_3 = sum(_is_set_won(s, 'home') for s in [s1, s2, s3])
            a_first_3 = sum(_is_set_won(s, 'away') for s in [s1, s2, s3])
            if h_first_3 == 2 and a_first_3 == 1:
                update_accumulators(current_game_diff, current_total_games, prob)
        
        # Check for Away 3-1
        # Away must win s4, and 2 of (s1,s2,s3), Home must win 1 of (s1,s2,s3)
        if _is_set_won(s4, 'away'):
            h_first_3 = sum(_is_set_won(s, 'home') for s in [s1, s2, s3])
            a_first_3 = sum(_is_set_won(s, 'away') for s in [s1, s2, s3])
            if a_first_3 == 2 and h_first_3 == 1:
                update_accumulators(current_game_diff, current_total_games, prob)

    # 5-Set Matches (Home 3-2 or Away 3-2)
    for s1, s2, s3, s4, s5 in product(all_set_scores, repeat=5):
        prob = set_score_probs[s1] * set_score_probs[s2] * set_score_probs[s3] * set_score_probs[s4] * set_score_probs[s5]
        current_total_games = games_total_map[s1] + games_total_map[s2] + games_total_map[s3] + games_total_map[s4] + games_total_map[s5]
        current_game_diff = game_diffs[s1] + game_diffs[s2] + game_diffs[s3] + game_diffs[s4] + game_diffs[s5]

        # Check for Home 3-2
        # Home must win s5, and 2 of (s1,s2,s3,s4), Away must win 2 of (s1,s2,s3,s4)
        if _is_set_won(s5, 'home'):
            h_first_4 = sum(_is_set_won(s, 'home') for s in [s1, s2, s3, s4])
            a_first_4 = sum(_is_set_won(s, 'away') for s in [s1, s2, s3, s4])
            if h_first_4 == 2 and a_first_4 == 2:
                update_accumulators(current_game_diff, current_total_games, prob)

        # Check for Away 3-2
        # Away must win s5, and 2 of (s1,s2,s3,s4), Home must win 2 of (s1,s2,s3,s4)
        if _is_set_won(s5, 'away'):
            h_first_4 = sum(_is_set_won(s, 'home') for s in [s1, s2, s3, s4])
            a_first_4 = sum(_is_set_won(s, 'away') for s in [s1, s2, s3, s4])
            if a_first_4 == 2 and h_first_4 == 2:
                update_accumulators(current_game_diff, current_total_games, prob)

    home_plus_75_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -7)
    home_plus_65_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -6)
    home_plus_55_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -5)
    home_plus_45_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -4)
    home_plus_35_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -3)
    home_plus_25_handicap_prob = sum(prob for diff, prob in cumulative_game_diff_probs.items() if diff >= -2)

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
