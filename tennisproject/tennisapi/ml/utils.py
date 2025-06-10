import logging
from datetime import timedelta

from django.db.models import Q
from psycopg2.extensions import AsIs
from tabulate import tabulate
from tennisapi.models import (
    Bet,
    BetWta,
    Match,
    Players,
    WtaMatch,
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


def _get_surface_from_user_input(tournament_name_hint):
    valid_surfaces = ["clay", "grass", "hard"]
    while True:
        prompt_message = (
            f"Surface for tournament '{tournament_name_hint}' could not be determined from DB or was invalid. "
            f"Please enter the surface ({', '.join(valid_surfaces)}): "
        )
        user_input = input(prompt_message).strip().lower()
        if user_input in valid_surfaces:
            log.info(
                f"User provided surface: {user_input} for tournament '{tournament_name_hint}'"
            )
            return user_input
        else:
            print(f"Invalid input. Please enter one of {', '.join(valid_surfaces)}.")


def define_surface(level, tour, from_at, input_surface):
    from_at = from_at - timedelta(days=10)
    tour_id = None
    tourney_name_from_db = None

    if level == "atp":
        qs_item = (
            Match.objects.filter(
                Q(tourney_name__icontains=tour)
                & ~Q(tourney_name__icontains="double")
                & Q(start_at__gte=from_at)
            )
            .values("surface", "tourney_name", "tour_id")
            .first()
        )
        log.info(f"Queried Match for ATP tournament '{tour}': {qs_item}")

        db_surface_value = None
        if qs_item:
            tour_id = qs_item.get("tour_id")
            tourney_name_from_db = qs_item.get("tourney_name")
            db_surface_value = qs_item.get("surface")

        if db_surface_value and isinstance(db_surface_value, str):
            normalized_surface = None
            if "clay" in db_surface_value.lower():
                normalized_surface = "clay"
            elif "grass" in db_surface_value.lower():
                normalized_surface = "grass"
            elif "hard" in db_surface_value.lower():
                normalized_surface = "hard"

            if normalized_surface:
                surface = normalized_surface
                log.info(
                    f"Determined surface from DB: {surface} for {tourney_name_from_db or tour}"
                )
            else:
                log.warning(
                    f"Unrecognized surface value '{db_surface_value}' in DB for {tourney_name_from_db or tour}. Asking user."
                )
                if input_surface:
                    surface = input_surface
                else:
                    surface = _get_surface_from_user_input(tourney_name_from_db or tour)
        else:
            if db_surface_value is None:
                log.warning(
                    f"Surface field is None in DB for ATP tournament '{tourney_name_from_db or tour}'. Asking user."
                )
            elif not qs_item:
                log.warning(
                    f"No DB record found for ATP tournament '{tour}'. Asking user."
                )
            else:  # Should not happen if db_surface_value is not str and not None
                log.warning(
                    f"Unexpected surface field type or value in DB for ATP tournament '{tourney_name_from_db or tour}'. Asking user."
                )
            if input_surface:
                surface = input_surface
            else:
                surface = _get_surface_from_user_input(tourney_name_from_db or tour)

    else:  # WTA
        qs_item = (
            WtaMatch.objects.filter(
                Q(tourney_name__icontains=tour)
                & ~Q(tourney_name__icontains="double")
                & Q(start_at__gte=from_at)
            )
            .values("surface", "tourney_name", "tour_id")
            .first()
        )
        log.info(f"Queried WtaMatch for WTA tournament '{tour}': {qs_item}")

        db_surface_value = None
        if qs_item:
            tour_id = qs_item.get("tour_id")
            tourney_name_from_db = qs_item.get("tourney_name")
            db_surface_value = qs_item.get("surface")

        if db_surface_value and isinstance(db_surface_value, str):
            normalized_surface = None
            if "clay" in db_surface_value.lower():
                normalized_surface = "clay"
            elif "grass" in db_surface_value.lower():
                normalized_surface = "grass"
            elif "hard" in db_surface_value.lower():
                normalized_surface = "hard"

            if normalized_surface:
                surface = normalized_surface
                log.info(
                    f"Determined surface from DB: {surface} for {tourney_name_from_db or tour}"
                )
            else:
                log.warning(
                    f"Unrecognized surface value '{db_surface_value}' in DB for {tourney_name_from_db or tour}. Asking user."
                )
                if input_surface:
                    surface = input_surface
                else:
                    surface = _get_surface_from_user_input(tourney_name_from_db or tour)
        else:
            if db_surface_value is None:
                log.warning(
                    f"Surface field is None in DB for WTA tournament '{tourney_name_from_db or tour}'. Asking user."
                )
            elif not qs_item:
                log.warning(
                    f"No DB record found for WTA tournament '{tour}'. Asking user."
                )
            else:  # Should not happen if db_surface_value is not str and not None
                log.warning(
                    f"Unexpected surface field type or value in DB for WTA tournament '{tourney_name_from_db or tour}'. Asking user."
                )
            if input_surface:
                surface = input_surface
            else:
                surface = _get_surface_from_user_input(tourney_name_from_db or tour)

    query_surface = surface
    final_tourney_name = tourney_name_from_db or tour

    return surface, query_surface, tour_id, final_tourney_name


def define_query_parameters(level, tour, now, end_at, surface=None):
    surface, query_surface, tour_id, tourney_name = define_surface(
        level, tour, now, surface
    )
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
        # 'home_id',
        # 'away_id',
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
