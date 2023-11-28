import json
import os
import time
import pandas as pd
import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from sportscore.models import Leagues, Events, Players, Teams, Stats
from tennisapi.models import AtpMatches, AtpTour, ChTour, WtaTour, WtaMatches
from tqdm import tqdm
from django.conf import settings
from vakio.task.winshare import get_win_share
from vakio.task.find_lines import find_lines
from vakio.task.probs import calculate_probabilities
from vakio.task.poisson import calculate_poisson
from vakio.task.match_prob import match_probability
from vakio.task.moniveto import moniveto
from vakio.task.moniveto_winshare import moniveto_winshares
from vakio.task.moniveto_bet import moniveto_bet


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

        list_sports_cmd = subparsers.add_parser("find-lines")
        list_sports_cmd.set_defaults(subcommand=self.find_profits)

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

        list_sports_cmd = subparsers.add_parser("moniveto-bet")
        list_sports_cmd.set_defaults(subcommand=self.place_moniveto_bet)


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
            print(row['name'], row['id'], row['listIndex'])

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
            print(row['id'], row['listIndex'], row['rows'][0])

    def get_winshare(self, options):
        get_win_share()

    def find_profits(self, options):
        find_lines()

    def calc_prob(self, options):
        calculate_probabilities()

    def calc_poisson(self, options):
        calculate_poisson()

    def calc_match_prob(self, options):
        match_probability()

    def calc_moniveto(self, options):
        moniveto()

    def get_moniveto_winshares(self, options):
        moniveto_winshares()

    def place_moniveto_bet(self, options):
        moniveto_bet()
