from django.db.models import Exists, OuterRef, Q
from tennisapi.models import (
    WtaClayElo,
    WtaGrassElo,
    WtaHardElo,
    WtaMatches,
    WTAPlayers,
    WtaTour,
)

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
    matches = (
        WtaMatches.objects.filter(
            surface__icontains=surface,
            round_name__isnull=False,
        )
        .filter(
            Q(round_name__icontains="Final")
            | Q(round_name__icontains="Semifinal")
            | Q(round_name__icontains="Quarterfinal")
            | Q(round_name__icontains="16")
            | Q(round_name__icontains="32")
            | Q(round_name__icontains="64")
            | Q(round_name__icontains="128")
        )
        .order_by("date", "match_num")
        .distinct()
    )

    if surface == "clay":
        matches = matches.filter(
            ~Exists(WtaClayElo.objects.filter(id=OuterRef("wtamatch")))
        )
        elo_table = WtaClayElo
    elif surface == "hard":
        matches = matches.filter(
            ~Exists(WtaHardElo.objects.filter(id=OuterRef("wtahardmatch")))
        )
        elo_table = WtaHardElo
    elif surface == "grass":
        matches = matches.filter(
            ~Exists(WtaGrassElo.objects.filter(id=OuterRef("wtagrassmatch")))
        )
        elo_table = WtaGrassElo
    else:
        return

    for match in matches:
        try:
            winner_id = WTAPlayers.objects.filter(id=match.winner_id)[0]
        except:
            continue
        try:
            loser_id = WTAPlayers.objects.filter(id=match.loser_id)[0]
        except:
            continue
        winner = elo_table.objects.filter(player__id=match.winner_id).order_by("-games")
        loser = elo_table.objects.filter(player__id=match.loser_id).order_by("-games")

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
            player=winner_id,
            match=match,
            elo=winner_elo,
            elo_change=winner_change,
            games=winner_games + 1,
            date=match.date,
        )
        m.save()

        # Loser
        k = calculate_k_factor(loser_games, o, c, s)
        loser_elo, loser_change = calculate_new_elo(loser_elo, 0, 1 - prob, k)

        m = elo_table(
            player=loser_id,
            match=match,
            elo=loser_elo,
            elo_change=loser_change,
            games=loser_games + 1,
            date=match.date,
        )
        m.save()

        print(
            match.id,
            match.date,
            match.surface,
            match.tourney_name,
            winner_id.last_name,
            round(winner_elo, 0),
            round(winner_elo - winner_change, 0),
            loser_id.last_name,
            round(loser_elo, 0),
            round(loser_elo - loser_change, 0),
        )
