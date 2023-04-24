from tennisapi.models import AtpElo, AtpTour, AtpMatches
from django.db.models import Q


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


def atp_elorate(surface):
    matches = AtpMatches.objects.filter(
        tour__surface__icontains=surface,
        round_name__isnull=False,
    ).filter(
        Q(round_name='Final') |
        Q(round_name='Semifinal') |
        Q(round_name='Quarterfinal') |
        Q(round_name='R16') |
        Q(round_name='R32') |
        Q(round_name='R64') |
        Q(round_name='R128')
    ).order_by('date', 'match_num')

    for match in matches:
        # Get elo from database
        winner = AtpElo.objects.filter(player__id=match.winner_id).order_by('-games')
        loser = AtpElo.objects.filter(player__id=match.loser_id).order_by('-games')
        if not winner:
            winner_elo = 1500
            winner_games = 0
        else:
            winner_elo = winner.elo
            winner_games = winner.games
        if not loser:
            loser_elo = 1500
            loser_games = 0
        else:
            loser_elo = loser.elo
            loser_games = loser.games

        prob = probability_of_winning(loser_elo, winner_elo)
        k = calculate_k_factor(player_matches, o, c, s)
        winner_elo, winner_change = calculate_new_elo(winner_elo, 1, prob, k)
        m = AtpElo(
            player=winner,
            elo=winner_elo,
            elo_change=winner_change,
            games=winner_games + 1,
        )
        m.save()
        print(prob)
        break