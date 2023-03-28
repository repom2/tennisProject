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
        file_name2 = "/app/tennisproject/tennis_atp/tennis_data/atp_players.csv"
        file_name = os.path.join(settings.BASE_DIR / "atp_players.csv")
        print(file_name2)
        tmp_data = pd.read_csv(file_name, sep=',')

        products = [
            Players(
                player_id=row['player_id'],
                name_first=row['name_first'],
                name_last=row['name_last'],
                hand=row['hand'],
                dob=row['dob'],
                ioc=row['ioc'],
                height=row['height'],
                wikidata_id=row['wikidata_id'],
            )
            for index, row in tmp_data.iterrows()
        ]
        Players.objects.bulk_create(products)
