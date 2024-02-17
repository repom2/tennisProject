from footballapi.models import Ligue1Elo, Ligue1, Teams
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


def ligue1_elorate():
    matches = Ligue1.objects.filter(winner_code__isnull=False).order_by('start_at').distinct()

    matches = matches.filter(
            ~Exists(Ligue1Elo.objects.filter(id=OuterRef('elo_rating_ligue1'))))
    elo_table = Ligue1Elo
    for match in matches:
        try:
            home_id = Teams.objects.filter(id=match.home_team_id)[0]
            away_id = Teams.objects.filter(id=match.away_team_id)[0]
        except:
            continue
        home = elo_table.objects.filter(team__id=match.home_team_id).order_by('-games')
        away = elo_table.objects.filter(team__id=match.away_team_id).order_by('-games')
        if match.winner_code == 1:
            winner = home
            winner_id = home_id
            loser = away
            loser_id = away_id
            winner_outcome = 1
            loser_outcome = 0
        elif match.winner_code == 2:
            winner = away
            winner_id = away_id
            loser = home
            loser_id = home_id
            winner_outcome = 1
            loser_outcome = 0
        elif match.winner_code == 3:
            winner = home
            winner_id = home_id
            loser = away
            loser_id = away_id
            winner_outcome = 0.5
            loser_outcome = 0.5
        else:
            continue
        if not winner:
            winner_elo = 1500
            winner_games = 0
        else:
            winner_elo = winner[0].elo
            winner_games = winner[0].games
        if not loser:
            loser_elo = 1500
            loser_games = 0
        else:
            loser_elo = loser[0].elo
            loser_games = loser[0].games
        prob = probability_of_winning(loser_elo, winner_elo)
        k = calculate_k_factor(winner_games, o, c, s)
        winner_elo, winner_change = calculate_new_elo(winner_elo, winner_outcome, prob, k)

        m = elo_table(
            team=winner_id,
            match=match,
            elo=winner_elo,
            elo_change=winner_change,
            games=winner_games + 1,
            date=match.start_at,
        )
        m.save()

        # Loser
        k = calculate_k_factor(loser_games, o, c, s)
        loser_elo, loser_change = calculate_new_elo(loser_elo, loser_outcome, 1 - prob, k)

        m = elo_table(
            team=loser_id,
            match=match,
            elo=loser_elo,
            elo_change=loser_change,
            games=loser_games + 1,
            date=match.start_at,
        )
        m.save()
        print(
            match.start_at.date(),
            match.name,
            winner_id.name,
            round(winner_elo, 0),
            round(winner_elo - winner_change, 0),
            loser_id.name,
            round(loser_elo, 0),
            round(loser_elo - loser_change, 0),
        )
