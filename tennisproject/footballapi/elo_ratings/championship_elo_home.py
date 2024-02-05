from footballapi.models import ChampionshipEloHome, ChampionshipEloAway, Championship, Teams
from django.db.models import Q, Exists, OuterRef


c = 250
o = 5
s = 0.4

def probability_of_winning(opponent, player):
    l = (opponent - player) / 400
    prob2win = 1 / (1 + 10 ** (l))
    return prob2win


def calculate_new_elo(elo_before, outcome, pwin, k):
    change = k * (outcome - pwin)
    new_elo = elo_before + change
    return new_elo, round(change, 0)


def calculate_k_factor(matches, o, c, s):
    k = c / (matches + o) ** s
    return k


def championship_elo_home():
    matches = Championship.objects.filter(winner_code__isnull=False).order_by('start_at').distinct()

    matches = matches.filter(
            ~Exists(ChampionshipEloHome.objects.filter(id=OuterRef('elo_rating_home'))))

    for match in matches:
        try:
            home_id = Teams.objects.filter(id=match.home_team_id)[0]
            away_id = Teams.objects.filter(id=match.away_team_id)[0]
        except:
            continue
        home = ChampionshipEloHome.objects.filter(team__id=match.home_team_id).order_by('-games')
        away = ChampionshipEloAway.objects.filter(team__id=match.away_team_id).order_by('-games')
        if match.winner_code == 1:
            outcome = 1
            away_outcome = 0
        elif match.winner_code == 2:
            outcome = 0
            away_outcome = 1
        elif match.winner_code == 3:
            outcome = 0.5
            away_outcome = 0.5
        else:
            continue
        if not home:
            home_elo = 1500
            home_games = 0
        else:
            home_elo = home[0].elo
            home_games = home[0].games
        if not away:
            away_elo = 1500
            away_games = 0
        else:
            away_elo = away[0].elo
            away_games = away[0].games
        prob = probability_of_winning(away_elo, home_elo)
        k = calculate_k_factor(home_games, o, c, s)
        home_elo, home_change = calculate_new_elo(home_elo, outcome, prob, k)

        m = ChampionshipEloHome(
            team=home_id,
            match=match,
            elo=home_elo,
            elo_change=home_change,
            games=home_games + 1,
            date=match.start_at,
        )
        m.save()

        # Loser
        k = calculate_k_factor(away_games, o, c, s)
        away_elo, away_change = calculate_new_elo(away_elo, away_outcome, 1 - prob, k)

        m = ChampionshipEloAway(
            team=away_id,
            match=match,
            elo=away_elo,
            elo_change=away_change,
            games=away_games + 1,
            date=match.start_at,
        )
        m.save()
        print(
            match.start_at.date(),
            match.name,
            home_id.name,
            round(home_elo, 0),
            round(home_elo - home_change, 0),
            away_id.name,
            round(away_elo, 0),
            round(away_elo - away_change, 0),
        )
