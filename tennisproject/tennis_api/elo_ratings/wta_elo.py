from tennis_api.models import WtaEloHard, WtaEloClay, WtaEloGrass, WtaTour, WtaMatch, Player
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


def wta_elorate(surface):
    matches = WtaMatch.objects.filter(
        tour__surface__icontains=surface,
        round_name__isnull=False,
        status='finished',
        winner_code__isnull=False,
    ).filter(
        ~Q(round_name__icontains='qualific')
    ).filter(Q(home_score=2) | Q(away_score=2)).order_by('start_at').distinct()
    print(len(matches))
    if surface == 'clay':
        matches = matches.filter(
            ~Exists(WtaEloClay.objects.filter(id=OuterRef('wta_elo_clay'))))
        elo_table = WtaEloClay
    elif surface == 'hard':
        matches = matches.filter(
            ~Exists(WtaEloHard.objects.filter(id=OuterRef('wta_elo_hard'))))
        elo_table = WtaEloHard
    elif surface == 'grass':
        matches = matches.filter(
            ~Exists(WtaEloGrass.objects.filter(id=OuterRef('wta_elo_grass'))))
        elo_table = WtaEloGrass
    else:
        print('Invalid surface')
        return
    print(len(matches))
    for match in matches:
        # Get elo from database
        tour = WtaTour.objects.filter(id=match.tour_id)[0]
        try:
            home_id = Player.objects.filter(id=match.home_id)[0]
            away_id = Player.objects.filter(id=match.away_id)[0]
        except Exception as e:
            print(e)
            continue
        home = elo_table.objects.filter(player__id=match.home_id).order_by('-games')
        away = elo_table.objects.filter(player__id=match.away_id).order_by('-games')
        if match.winner_code == 1:
            winner = home
            loser = away
        elif match.winner_code == 2:
            winner = away
            loser = home
        else:
            print('No winner')
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
        winner_elo, winner_change = calculate_new_elo(winner_elo, 1, prob, k)

        m = elo_table(
            player=home_id,
            match=match,
            elo=winner_elo,
            elo_change=winner_change,
            games=winner_games + 1,
            date=match.start_at,
        )
        m.save()

        # Loser
        k = calculate_k_factor(loser_games, o, c, s)
        loser_elo, loser_change = calculate_new_elo(loser_elo, 0, 1 - prob, k)

        m = elo_table(
            player=away_id,
            match=match,
            elo=loser_elo,
            elo_change=loser_change,
            games=loser_games + 1,
            date=match.start_at,
        )
        m.save()
        print(
            match.start_at,
            tour.surface,
            tour.slug,
            home_id.name,
            round(winner_elo, 0),
            round(winner_elo - winner_change, 0),
            away_id.name,
            round(loser_elo, 0),
            round(loser_elo - loser_change, 0),
        )
