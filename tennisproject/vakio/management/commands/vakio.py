import json
import os
import time
import pandas as pd
import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from vakio.models import Moniveto
from tqdm import tqdm
from django.conf import settings
from vakio.task.winshare import get_win_share
from vakio.task.find_lines import find_lines
from vakio.task.probs import calculate_probabilities
from vakio.task.moniveto.poisson import calculate_poisson
from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.moniveto import moniveto
from vakio.task.moniveto.moniveto_winshare import moniveto_winshares
from vakio.task.moniveto.moniveto_bet import moniveto_bet
from vakio.task.moniveto.parse_odds import parse_odds
import logging
from tabulate import tabulate
import pytz
import datetime
from django.utils import timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s: %(message)s'
)

logger = logging.getLogger('MyLogger')

pd.set_option('display.max_columns', None)


def login(username, password):
    s = requests.Session()
    login_req = {
        "type": "STANDARD_LOGIN",
        "login": username,
        "password": password
    }
    r = s.post(
        "https://www.veikkaus.fi/api/bff/v1/sessions",
        data=json.dumps(login_req),
        headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-ESA-API-Key': 'ROBOT'
        }
    )
    if r.status_code == 200:
        return s
    else:
        raise Exception("Authentication failed", r.status_code)


class Command(BaseCommand):
    """Vakio commands."""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        list_sports_cmd = subparsers.add_parser("sports")
        list_sports_cmd.set_defaults(subcommand=self.list_sports)

        list_sports_cmd = subparsers.add_parser("winshare")
        list_sports_cmd.set_defaults(subcommand=self.get_winshare)
        list_sports_cmd.add_argument("bet", nargs='?', type=str,
                                     help='If not provided no bets', default=None)
        list_sports_cmd.add_argument("stake", nargs='?', type=int, default=30)
        list_sports_cmd.add_argument("index", nargs='?', type=int, default=None)
        list_sports_cmd.add_argument("id", nargs='?', type=int, default=None)

        list_sports_cmd = subparsers.add_parser("find-lines")
        list_sports_cmd.set_defaults(subcommand=self.find_profits)
        list_sports_cmd.add_argument("bet", nargs='?', type=str,
                                     help='If not provided no bets', default=None)
        list_sports_cmd.add_argument("stake", nargs='?', type=int, default=30)
        list_sports_cmd.add_argument("index", nargs='?', type=int, default=None)
        list_sports_cmd.add_argument("id", nargs='?', type=int, default=None)

        list_sports_cmd = subparsers.add_parser("prob")
        list_sports_cmd.set_defaults(subcommand=self.calc_prob)

        list_sports_cmd = subparsers.add_parser("poisson")
        list_sports_cmd.set_defaults(subcommand=self.calc_poisson)

        list_sports_cmd = subparsers.add_parser("match-prob")
        list_sports_cmd.set_defaults(subcommand=self.calc_match_prob)

        list_sports_cmd = subparsers.add_parser("moniveto")
        list_sports_cmd.set_defaults(subcommand=self.calc_moniveto)

        list_sports_cmd = subparsers.add_parser("moniveto-winshares")
        list_sports_cmd.set_defaults(subcommand=self.get_moniveto_winshares)

        list_sports_cmd = subparsers.add_parser("moni-bet")
        list_sports_cmd.set_defaults(subcommand=self.place_moniveto)
        list_sports_cmd.add_argument("bet", nargs='?', type=str,
                                 help='If not provided no bets', default=None)
        list_sports_cmd.add_argument("stake", nargs='?', type=int, default=35)
        list_sports_cmd.add_argument("index", nargs='?', type=int, default=None)
        list_sports_cmd.add_argument("id", nargs='?', type=int, default=None)

        list_sports_cmd = subparsers.add_parser("moniveto-bet")
        list_sports_cmd.set_defaults(subcommand=self.place_moniveto_bet)
        list_sports_cmd.add_argument("bet", nargs='?', type=str,
                                     help='If not provided no bets', default=None)
        list_sports_cmd.add_argument("stake", nargs='?', type=int, default=30)
        list_sports_cmd.add_argument("index", nargs='?', type=int, default=None)
        list_sports_cmd.add_argument("id", nargs='?', type=int, default=None)

        list_sports_cmd = subparsers.add_parser("parse-odds")
        list_sports_cmd.set_defaults(subcommand=self.parse_score_odds)


    def handle(self, *args, **options):
        options["subcommand"](options)

    def list_sports(self, options):

        s = login("repom", "_W14350300n1")

        response = s.get(
            'https://www.veikkaus.fi/api/sport-open-games/v1/games/SPORT/draws',
            headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-ESA-API-Key': 'ROBOT'
            }
        )

        data = response.text
        data = json.loads(data)
        for row in data:
            logger.info(
                row['name'] + ' ' + str(row['id']) + ' ' + str(row['listIndex']))
            close = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(row['closeTime'] / 1000)
            )
            prize = row['gameRuleSet']['basePrice']
            outcomes = row['rows']
            for i, outcome in enumerate(outcomes, 1):
                home = outcome['outcome']['home']['name']
                away = outcome['outcome']['away']['name']
                logger.info(str(i) + '. ' + home + '-' + away)
                if i == 3 or i == 6 or i == 9:
                    logger.info('-' * 50)
            logger.info('-' * 50)

        response = s.get(
            'https://www.veikkaus.fi/api/sport-open-games/v1/games/MULTISCORE/draws',
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json',
                'X-ESA-API-Key': 'ROBOT'
            }
        )

        data = response.text
        data = json.loads(data)
        for row in data:
            logging.info(str(row['id']) + ' ' + str(row['listIndex']))

            # Your original code to get the time
            timestamp = time.localtime(row['closeTime'] / 1000)
            close_naive = time.strftime('%Y-%m-%d %H:%M:%S', timestamp)
            close = timezone.make_aware(
                datetime.datetime.strptime(close_naive, '%Y-%m-%d %H:%M:%S'),
                timezone=pytz.timezone('UTC')
            )
            stake = row['gameRuleSet']['minStake']
            outcomes = row['rows']  # ['outcome']
            Moniveto.objects.update_or_create(
                moniveto_id=row['id'],
                list_index=row['listIndex'],
                defaults={
                    'close': close,
                    'stake': stake,
                }
            )
            for i, outcome in enumerate(outcomes):
                #logger.info(outcome)
                home = outcome['outcome']['home']['name']
                away = outcome['outcome']['away']['name']
                logger.info(home + '-' + away)
                away_field = 'away' + str(i+1)
                home_field = 'home' + str(i+1)
                Moniveto.objects.update_or_create(
                    moniveto_id=row['id'],
                    list_index=row['listIndex'],
                    defaults={
                        away_field: away,
                        home_field: home
                    }
                )
            logger.info('-' * 50)

    def get_winshare(self, options):
        bet = options["bet"]
        max_bet_eur = options["stake"]
        list_index = options["index"]
        vakio_id = options["id"]
        get_win_share(list_index, vakio_id)
        find_lines(list_index, vakio_id, max_bet_eur, bet)

    def find_profits(self, options):
        bet = options["bet"]
        max_bet_eur = options["stake"]
        list_index = options["index"]
        vakio_id = options["id"]
        find_lines(list_index, vakio_id, max_bet_eur, bet)

    def calc_prob(self, options):
        calculate_probabilities()

    def calc_poisson(self, options):
        calculate_poisson()

    def calc_match_prob(self, options):
        match_probability()

    def calc_moniveto(self, options):
        moniveto()

    def get_moniveto_winshares(self, options):
        moniveto_winshares(None, None)

    def place_moniveto_bet(self, options):
        bet = options["bet"]
        stake = options["stake"]
        index = options["index"]
        id = options["id"]
        moniveto_bet(bet, stake, index, id)

    def place_moniveto(self, options):
        bet = options["bet"]
        stake = options["stake"]
        index = options["index"]
        id = options["id"]
        moniveto_winshares(index, id)
        moniveto_bet(bet, stake, index, id)

    def parse_score_odds(self, options):
        parse_odds()
