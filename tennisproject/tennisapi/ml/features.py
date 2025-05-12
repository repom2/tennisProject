common_features = ["round_name"]
selected_features = [
    "hard_elo",
    "grass_elo",
    "games",
    "year_games",
    "year_elo",
    "win_percent",
    "win_grass_percent",
    "court_time",
]


def winner_features():
    feature_list = []
    for feature in selected_features:
        feature_list.append("winner_" + feature)
    return feature_list


def loser_features():
    feature_list = []
    for feature in selected_features:
        feature_list.append("loser_" + feature)
    return feature_list


def features():
    feature_list = common_features + winner_features() + loser_features()
    return feature_list
