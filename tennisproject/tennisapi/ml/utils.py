import logging

from psycopg2.extensions import AsIs
from tennisapi.models import Bet, BetWta, Match, Players, WtaMatch, WTAPlayers
from tabulate import tabulate

log = logging.getLogger(__name__)


def probability_of_winning(x):
    l_param = (x) / 400
    prob2win = 1 / (1 + 10 ** (l_param))
    return 1 - prob2win


def label_round(data, mapping):
    data["round_name"] = data["round_name"].map(mapping)
    return data


def define_surface(level, tour, from_at):
    if level == "atp":
        qs = (
            Match.objects.filter(tourney_name__icontains=tour, start_at__gte=from_at)
            .values_list("surface", flat=True)
            .first()
        )
        if qs is None:
            surface = "grass"
            logging.info("Surface not found: %s", surface)
        elif "clay" in qs or "Clay" in qs:
            surface = "clay"
        elif "grass" in qs or "Grass" in qs:
            surface = "grass"
        elif "hard" in qs or "Hard" in qs:
            surface = "hard"
        else:
            logging.info("Surface not found: %s", qs)
            exit()
        query_surface = surface

    else:
        qs = (
            WtaMatch.objects.filter(tourney_name__icontains=tour, start_at__gte=from_at)
            .values_list("surface", flat=True)
            .first()
        )
        try:
            if "clay" in qs or "Clay" in qs:
                surface = "clay"
            elif "grass" in qs or "Grass" in qs:
                surface = "grass"
            elif "hard" in qs or "Hard" in qs:
                surface = "hard"
            else:
                logging.info("Surface not found: %s", qs)
                exit()
            query_surface = surface
        except TypeError:
            logging.info("No surface found!")
            # let user input surface
            surface = input("Enter surface: ")
            # empty query string for asiIs
            query_surface = AsIs("")
    return surface, query_surface


def define_query_parameters(level, tour, now, end_at):
    if level == "atp":
        surface, query_surface = define_surface(level, tour, now)
        bet_qs = Bet.objects.all()
        match_qs = Match.objects.all()
        player_qs = Players.objects.all()
        tour_table = "tennisapi_atptour"
        matches_table = "tennisapi_atpmatches"
        match_table = "tennisapi_match"
        player_table = "tennisapi_players"
        hard_elo = "tennisapi_atphardelo"
        grass_elo = "tennisapi_atpgrasselo"
        clay_elo = "tennisapi_atpelo"
        bet_table = "tennisapi_bet"
    else:
        surface, query_surface = define_surface(level, tour, now)
        bet_qs = BetWta.objects.all()
        match_qs = WtaMatch.objects.all()
        player_qs = WTAPlayers.objects.all()
        tour_table = "tennisapi_wtatour"
        matches_table = "tennisapi_wtamatches"
        match_table = "tennisapi_wtamatch"
        player_table = "tennisapi_wtaplayers"
        hard_elo = "tennisapi_wtahardelo"
        grass_elo = "tennisapi_wtagrasselo"
        clay_elo = "tennisapi_wtaelo"
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
