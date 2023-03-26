import pandas as pd
import json
import os
from django.conf import settings

import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from tennis_atp.models import Players
from tqdm import tqdm

pd.set_option('display.max_columns', None)


class Command(BaseCommand):
    """ATP Data"""
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        list_players_cmd = subparsers.add_parser("players")
        list_players_cmd.set_defaults(subcommand=self.list_players)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def list_players(self, options):
        file_name = "tennisproject/tennis_atp/tennis_data/atp_players.csv"
        file_name = os.path.join(settings.BASE_DIR / file_name)
        print(file_name)
        tmp_data = pd.read_csv(file_name, sep=';')

        products = [
            Players(
                player_id=tmp_data.ix[row]['player_id'],
                name_first=tmp_data.ix[row]['name_first'],
                name_last=tmp_data.ix[row]['name_last'],
                hand=tmp_data.ix[row]['hand'],
                dob=tmp_data.ix[row]['dob'],
                ioc=tmp_data.ix[row]['ioc'],
                height=tmp_data.ix[row]['height'],
                wikidata_id=tmp_data.ix[row]['wikidata_id'],
            )
            for row in tmp_data
        ]
        Players.objects.bulk_create(products)
