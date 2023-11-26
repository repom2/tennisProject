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

pd.set_option('display.max_columns', None)


def login (username, password):
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
        data_df = data['data']
        df = pd.DataFrame(data_df)
        print(df)

