import logging
from datetime import datetime, timedelta

from django.db.models import Q
from psycopg2.extensions import AsIs
from tabulate import tabulate
from tennisapi.models import (
    AtpMatches,
    Bet,
    BetWta,
    Match,
    Players,
    WtaMatch,
    WtaMatches,
    WTAPlayers,
)

log = logging.getLogger(__name__)


def probability_of_winning(x):
    l_param = (x) / 400
    prob2win = 1 / (1 + 10 ** (l_param))
    return 1 - prob2win


def label_round(data, mapping):
    data["round_name"] = data["round_name"].map(mapping)
    return data


def define_surface(level, tour, from_at):
    from_at = from_at - timedelta(days=10)
    if level == "atp":
        qs = Match.objects.filter(
            Q(tourney_name__icontains=tour)
            & ~Q(tourney_name__icontains="double")
            & Q(start_at__gte=from_at)
            # & Q(surface__isnull=False)
        ).values("surface", "tourney_name", "tour_id")[2]
        log.info(qs)
        log.info("level: %s", level)
        if qs is None:
            logging.info("qs not found: %s", qs)
            exit()
        surface = qs["surface"]
        if surface is None:
            logging.info("Surface not found: %s", qs)
            if "stuttgart" in qs["tourney_name"]:
                logging.info("Surface not found: %s", qs)
                surface = "clay"
                logging.info("Surface is hard")
            else:
                logging.info("Surface not found: %s", qs)
                exit()
        tour_id = qs["tour_id"]
        tourney_name = qs["tourney_name"]

        if "clay" in surface or "Clay" in surface:
            surface = "clay"
        elif "grass" in surface or "Grass" in surface:
            surface = "grass"
        elif "hard" in surface or "Hard" in surface:
            surface = "hard"
        else:
            logging.info("Surface not found: %s", qs)
            exit()
        query_surface = surface
    else:
        qs = (
            WtaMatch.objects.filter(
                Q(tourney_name__icontains=tour)
                & ~Q(tourney_name__icontains="double")
                & Q(start_at__gte=from_at)
                # & Q(surface__isnull=False)
            )
            .values("surface", "tourney_name", "tour_id")
            .first()
        )

        if qs is None:
            logging.info("Queryset not found: %s", qs)
            exit()
        surface = qs["surface"]
        logging.info("surface: %s", surface)
        if surface is None:
            logging.info("Surface not found: %s", qs)
            surface = "clay"
            # exit()
        tour_id = qs["tour_id"]
        tourney_name = qs["tourney_name"]

        if "clay" in surface or "Clay" in surface:
            surface = "clay"
        elif "grass" in surface or "Grass" in surface:
            surface = "grass"
        elif "hard" in surface or "Hard" in surface:
            surface = "hard"
        else:
            logging.info("Surface not found: %s", qs)
            exit()
        query_surface = surface

    return surface, query_surface, tour_id, tourney_name


def define_query_parameters(level, tour, now, end_at):
    surface, query_surface, tour_id, tourney_name = define_surface(level, tour, now)
    if level == "atp":
        bet_qs = Bet.objects.all()
        match_qs = Match.objects.all()
        player_qs = Players.objects.all()
        tour_table = "tennisapi_atptour"
        matches_table = "tennisapi_atpmatches"
        match_table = "tennisapi_match"
        player_table = "tennisapi_players"
        hard_elo = "tennisapi_atphardelo"
        grass_elo = "tennisapi_atpgrasselo"
        clay_elo = "tennisapi_atpclayelo"
        bet_table = "tennisapi_bet"
    else:
        bet_qs = BetWta.objects.all()
        match_qs = WtaMatch.objects.all()
        player_qs = WTAPlayers.objects.all()
        tour_table = "tennisapi_wtatour"
        matches_table = "tennisapi_wtamatches"
        match_table = "tennisapi_wtamatch"
        player_table = "tennisapi_wtaplayers"
        hard_elo = "tennisapi_wtahardelo"
        grass_elo = "tennisapi_wtagrasselo"
        clay_elo = "tennisapi_wtaclayelo"
        bet_table = "tennisapi_betwta"
    date = "2015-1-1"
    params = {
        "tour_table": AsIs(tour_table),
        "matches_table": AsIs(matches_table),
        "player_table": AsIs(player_table),
        "match_table": AsIs(match_table),
        "hard_elo": AsIs(hard_elo),
        "grass_elo": AsIs(grass_elo),
        "clay_elo": AsIs(clay_elo),
        "tour": AsIs(tour),
        "start_at": now,
        "end_at": end_at,
        "surface": AsIs(surface),
        "query_surface": AsIs(query_surface),
        "bet_table": AsIs(bet_table),
        "event": AsIs(tour),
        "date": date,
        "event_id": AsIs(tour_id),
        "tourney_name": AsIs(tourney_name),
    }
    log.info("Surface: %s", surface)
    return params, match_qs, bet_qs, player_qs, surface


def print_dataframe(data):
    columns = [
        "start_at",
        "winner_fullname",
        "loser_fullname",
        #'home_id',
        #'away_id',
        "home_player_id",
        "away_player_id",
        "home_fullname",
        "away_fullname",
        "atp_home_fullname",
        "atp_away_fullname",
    ]

    log.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}"
    )
