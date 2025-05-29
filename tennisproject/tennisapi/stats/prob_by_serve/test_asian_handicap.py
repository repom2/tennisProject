import unittest
from tennisproject.tennisapi.stats.prob_by_serve.asian_handicap import (
    _is_set_won,
    asian_handicap,
    asian_handicap_prob_best_of_five,
)

class TestIsSetWon(unittest.TestCase):
    def test_home_wins_set(self):
        self.assertTrue(_is_set_won("60", "home"))
        self.assertTrue(_is_set_won("64", "home"))
        self.assertTrue(_is_set_won("75", "home"))
        self.assertTrue(_is_set_won("76", "home"))

    def test_home_loses_set(self):
        self.assertFalse(_is_set_won("06", "home"))
        self.assertFalse(_is_set_won("46", "home"))
        self.assertFalse(_is_set_won("57", "home"))
        self.assertFalse(_is_set_won("67", "home"))
        self.assertFalse(_is_set_won("66", "home")) # Game not over

    def test_away_wins_set(self):
        self.assertTrue(_is_set_won("06", "away"))
        self.assertTrue(_is_set_won("46", "away"))
        self.assertTrue(_is_set_won("57", "away"))
        self.assertTrue(_is_set_won("67", "away"))

    def test_away_loses_set(self):
        self.assertFalse(_is_set_won("60", "away"))
        self.assertFalse(_is_set_won("64", "away"))
        self.assertFalse(_is_set_won("75", "away"))
        self.assertFalse(_is_set_won("76", "away"))
        self.assertFalse(_is_set_won("66", "away")) # Game not over

class TestAsianHandicapCalculations(unittest.TestCase):
    def setUp(self):
        # Simplified set score probabilities for testing
        # Home wins a set 80% of the time (score "60"), Away wins 20% (score "06")
        self.simple_set_probs = {
            "60": 0.8,  # Home wins set 6-0
            "06": 0.2   # Away wins set 6-0
        }
        # game_diffs = {"60": 6, "06": -6}
        # games_total_map = {"60": 6, "06": 6}

        # More complex set score probabilities for testing "over" scenarios
        self.detailed_set_probs = {
            "60": 0.3, # H win, 6 games, diff 6
            "64": 0.3, # H win, 10 games, diff 2
            "76": 0.2, # H win, 13 games, diff 1
            "06": 0.05,# A win, 6 games, diff -6
            "46": 0.05,# A win, 10 games, diff -2
            "67": 0.1, # A win, 13 games, diff -1
        } # Sum = 1.0

    def test_asian_handicap_best_of_3_simple_probs(self):
        # Expected values based on self.simple_set_probs
        # H wins 2-0: P("60","60") = 0.8 * 0.8 = 0.64. Diff=12, Games=12
        # A wins 2-0: P("06","06") = 0.2 * 0.2 = 0.04. Diff=-12, Games=12
        # H wins 2-1:
        #   P("60","06","60") = 0.8*0.2*0.8 = 0.128. Diff=6, Games=18
        #   P("06","60","60") = 0.2*0.8*0.8 = 0.128. Diff=6, Games=18
        #   Total P(H 2-1) = 0.256
        # A wins 2-1:
        #   P("60","06","06") = 0.8*0.2*0.2 = 0.032. Diff=-6, Games=18
        #   P("06","60","06") = 0.2*0.8*0.2 = 0.032. Diff=-6, Games=18
        #   Total P(A 2-1) = 0.064
        # cumulative_game_diff_probs: {12: 0.64, -12: 0.04, 6: 0.256, -6: 0.064}

        # home_plus_X_handicap_prob (diff >= -X_val):
        # >= -7: P(12)+P(6)+P(-6) = 0.64+0.256+0.064 = 0.96
        # >= -6: P(12)+P(6)+P(-6) = 0.96
        # >= -5: P(12)+P(6) = 0.64+0.256 = 0.896
        # >= -4: P(12)+P(6) = 0.896
        # >= -3: P(12)+P(6) = 0.896
        # >= -2: P(12)+P(6) = 0.896
        expected_handicaps = [0.96, 0.96, 0.896, 0.896, 0.896, 0.896]

        # Over games:
        # Games=12 (P=0.64+0.04=0.68), Games=18 (P=0.256+0.064=0.32)
        # All outcomes are <= 18 games.
        expected_overs = [0.0, 0.0, 0.0, 0.0, 0.0] # for 21.5, 22.5, 23.5, 24.5, 25.5

        results = asian_handicap(self.simple_set_probs)
        for i in range(6):
            self.assertAlmostEqual(results[i], expected_handicaps[i], places=5)
        for i in range(5):
            self.assertAlmostEqual(results[6+i], expected_overs[i], places=5)

    def test_asian_handicap_prob_best_of_five_simple_probs(self):
        # Expected values based on self.simple_set_probs
        # H 3-0: P("60","60","60") = 0.8^3 = 0.512. Diff=18, Games=18
        # A 3-0: P("06","06","06") = 0.2^3 = 0.008. Diff=-18, Games=18
        # H 3-1 (3 ways: AHHH, HAHH, HHHA - H wins last set): 3 * (0.2 * 0.8^3) = 3 * 0.1024 = 0.3072. Diff=12, Games=24
        # A 3-1 (3 ways: HAAA, AHAA, AAHA - A wins last set): 3 * (0.8 * 0.2^3) = 3 * 0.0064 = 0.0192. Diff=-12, Games=24
        # H 3-2 (C(4,2)=6 ways for first 4 sets, H wins 2, A wins 2, H wins 5th): 6 * (0.8^3 * 0.2^2) = 6 * 0.02048 = 0.12288. Diff=6, Games=30
        # A 3-2 (C(4,2)=6 ways for first 4 sets, A wins 2, H wins 2, A wins 5th): 6 * (0.2^3 * 0.8^2) = 6 * 0.00512 = 0.03072. Diff=-6, Games=30
        # cumulative_game_diff_probs: {18:0.512, -18:0.008, 12:0.3072, -12:0.0192, 6:0.12288, -6:0.03072}

        # home_plus_X_handicap_prob (diff >= -X_val):
        # >= -7: P(all positive diffs) + P(-6) = 0.512+0.3072+0.12288 + 0.03072 = 0.9728
        # >= -6: P(all positive diffs) + P(-6) = 0.9728
        # >= -5: P(all positive diffs) = 0.512+0.3072+0.12288 = 0.94208
        expected_handicaps = [0.9728, 0.9728, 0.94208, 0.94208, 0.94208, 0.94208]

        # Over games:
        # Games=18 (P=0.512+0.008=0.52)
        # Games=24 (P=0.3072+0.0192=0.3264)
        # Games=30 (P=0.12288+0.03072=0.1536)
        # prob_over_215: P(24g) + P(30g) = 0.3264 + 0.1536 = 0.48
        # prob_over_225: P(24g) + P(30g) = 0.48
        # prob_over_235: P(24g) + P(30g) = 0.48
        # prob_over_245: P(30g) = 0.1536
        # prob_over_255: P(30g) = 0.1536
        expected_overs = [0.48, 0.48, 0.48, 0.1536, 0.1536]

        results = asian_handicap_prob_best_of_five(self.simple_set_probs)
        for i in range(6):
            self.assertAlmostEqual(results[i], expected_handicaps[i], places=5)
        for i in range(5):
            self.assertAlmostEqual(results[6+i], expected_overs[i], places=5)

    def test_asian_handicap_best_of_3_detailed_probs_overs(self):
        # This test focuses on "over" calculations with more varied game counts per set.
        # Manual calculation for detailed_set_probs is complex, so we'll check a few properties
        # or specific simple scenarios if possible.
        # For now, just run it to ensure no errors and check if sum of probabilities is reasonable.
        # A full verification would require extensive manual calculation or a reference implementation.

        results = asian_handicap(self.detailed_set_probs)
        
        # Probabilities should be between 0 and 1
        for val in results:
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

        # Handicap probabilities should be non-increasing as the handicap becomes less favorable for home
        # results[0] (home_plus_75) >= results[1] (home_plus_65) ...
        for i in range(5): # Check up to home_plus_25
            self.assertGreaterEqual(results[i] + 1e-9, results[i+1]) # Add epsilon for float comparison

        # Over probabilities should be non-increasing as the threshold increases
        # results[6] (over 21.5) >= results[7] (over 22.5) ...
        for i in range(6, 10): # Check up to over 25.5
             self.assertGreaterEqual(results[i] + 1e-9, results[i+1])


    def test_asian_handicap_prob_best_of_five_detailed_probs_overs(self):
        results = asian_handicap_prob_best_of_five(self.detailed_set_probs)
        
        for val in results:
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

        for i in range(5):
            self.assertGreaterEqual(results[i] + 1e-9, results[i+1])
        
        for i in range(6, 10):
             self.assertGreaterEqual(results[i] + 1e-9, results[i+1])


if __name__ == '__main__':
    unittest.main()
