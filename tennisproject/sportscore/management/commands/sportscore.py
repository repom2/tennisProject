import json
import os

import pandas as pd
import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from sportscore.models import Leagues
from tqdm import tqdm

pd.set_option('display.max_columns', None)


class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        list_sports_cmd = subparsers.add_parser("sports")
        list_sports_cmd.set_defaults(subcommand=self.list_sports)

        list_sections_cmd = subparsers.add_parser("sections")
        list_sections_cmd.set_defaults(subcommand=self.list_sections)

        list_leagues_cmd = subparsers.add_parser("leagues")
        list_leagues_cmd.set_defaults(subcommand=self.list_leagues)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def list_sports(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports"
        sport_score_key = os.getenv('SPORT_SCORE_KEY')
        headers = {
            "X-RapidAPI-Key": "a4d03aeecbmsh56ecc366e6cbecbp1d03c0jsn366ab7c0dc51",
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)

        data = response.text
        data = json.loads(data)
        data_df = data['data']
        df = pd.DataFrame(data_df)
        print(df)

    def list_sections(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/sections"
        sport_score_key = os.getenv('SPORT_SCORE_KEY')
        headers = {
            "X-RapidAPI-Key": "a4d03aeecbmsh56ecc366e6cbecbp1d03c0jsn366ab7c0dc51",
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        response = requests.request(
            "GET", url, headers=headers)

        data = response.text
        data = json.loads(data)
        data_df = data['data']
        df = pd.DataFrame(data_df)
        print(df)

    def list_leagues(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/leagues"
        sport_score_key = os.getenv('SPORT_SCORE_KEY')
        headers = {
            "X-RapidAPI-Key": "a4d03aeecbmsh56ecc366e6cbecbp1d03c0jsn366ab7c0dc51",
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        querystring = {"page": "1"}

        response = requests.request(
            "GET", url, headers=headers, params=querystring
        )

        data = response.text
        data = json.loads(data)
        data_df = data['data']
        last_page = data['meta']["last_page"]
        print(last_page)
        print(data_df)

        for item in data_df:
            print(item)
            m = Leagues(**item)
            m.save()

        """with tqdm(total=last_page) as pbar:
            for page in range(1, last_page+1):
                querystring = {"page": str(page)}
                response = requests.request(
                    "GET", url, headers=headers, params=querystring
                )
                data = response.text
                data = json.loads(data)
                try:
                    data_df.extend(data["data"])
                except KeyError:
                    print(data_df)
                    pass
                pbar.update(1)

        with tqdm(total=len(data_df)) as pbar:
            for item in data_df:
                m = Leagues(**item)
                m.save()
                pbar.update(1)"""
