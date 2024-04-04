from footballapi.models import BetFootball
from icehockeyapi.models import BetIceHockey
import logging
import unicodedata
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

def name_decoder(name):
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')


def get_calc_probs(bet_table, home_name, away_name, columns):
    try:
        match_data = list(bet_table.objects.filter(
                (Q(home_name__icontains=home_name) |
                Q(away_name__icontains=away_name) ) &
                Q(start_at__gt=timezone.now() - timedelta(days=1))
            ).values_list(*columns).first())
    except TypeError:
        logging.info(f"No Match found: {home_name} - {away_name} ")
        match_data = [None]

    return match_data


def calc_probs(qs, sport):
    if sport == 'football':
        bet_table = BetFootball
    elif sport == 'hockey':
        bet_table = BetIceHockey
    else:
        print("sport not found!")
        return
    lst = []
    columns = [
        'home_prob',
        'draw_prob',
        'away_prob',
        'level',
        'home_poisson',
        'draw_poisson',
        'away_poisson',
        'home_est_goals',
        'away_est_goals',
        'home_goals',
        'home_conceded',
        'away_goals',
        'away_conceded',
        ]

    home_name = name_decoder(qs['home1'])
    away_name = name_decoder(qs['away1'])
    probs1 = get_calc_probs(bet_table, home_name, away_name, columns)

    logging.info(f"{qs['home1']} - {qs['away1']} {probs1}")
    lst.append([0] + probs1)

    home_name = name_decoder(qs['home2'])
    away_name = name_decoder(qs['away2'])
    probs2 = get_calc_probs(bet_table, home_name, away_name, columns)

    logging.info(f"{qs['home2']} - {qs['away2']} {probs2}")
    lst.append([1] + probs2)

    home_name = name_decoder(qs['home3'])
    away_name = name_decoder(qs['away3'])
    probs3 = get_calc_probs(bet_table, home_name, away_name, columns)
    logging.info(f"{qs['home3']} - {qs['away3']} {probs3}")
    lst.append([2] + probs3)
    if qs['home4']:
        home_name = name_decoder(qs['home4'])
        away_name = name_decoder(qs['away4'])
        probs4 = get_calc_probs(bet_table, home_name, away_name, columns)
        logging.info(f"{qs['home4']} - {qs['away4']} {probs4}")
        lst.append([3] + probs4)
