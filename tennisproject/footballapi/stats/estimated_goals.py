

def estimated_goals(
        league_avg_home_goals,
        league_avg_away_goals,
        home_team_goals,
        home_team_conceded,
        away_team_goals,
        away_team_conceded,
):
    home = home_team_goals / league_avg_home_goals
    home_defence = home_team_conceded / league_avg_away_goals

    away = away_team_goals / league_avg_away_goals
    away_defence = away_team_conceded / league_avg_home_goals

    home_est_goals = home * away_defence * league_avg_home_goals
    away_est_goals = away * home_defence * league_avg_away_goals

    return round(home_est_goals, 2), round(away_est_goals, 2)