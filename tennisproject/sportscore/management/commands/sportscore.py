import json
import os

import pandas as pd
import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from sportscore.models import Leagues, Events, Players, Teams
from tennisapi.models import AtpTour, ChTour, WtaTour
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

        events_by_leagues_cmd = subparsers.add_parser("events-by-leagues")
        events_by_leagues_cmd.set_defaults(subcommand=self.events_by_leagues)

        events_by_section_cmd = subparsers.add_parser("events-by-section")
        events_by_section_cmd.set_defaults(subcommand=self.events_by_section_id)

        list_events_cmd = subparsers.add_parser("events")
        list_events_cmd.set_defaults(subcommand=self.list_events)

        list_players_cmd = subparsers.add_parser("players")
        list_players_cmd.set_defaults(subcommand=self.list_players)

        event_players_cmd = subparsers.add_parser("tennis-players")
        event_players_cmd.set_defaults(subcommand=self.event_players)

        list_teams_cmd = subparsers.add_parser("teams")
        list_teams_cmd.set_defaults(subcommand=self.list_teams)

    def handle(self, *args, **options):
        options["subcommand"](options)

    # NO NEED
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

    # SECTION ID
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

        with tqdm(total=last_page) as pbar:
            for page in range(2, last_page+1):
                querystring = {"page": str(page)}
                response = requests.request(
                    "GET", url, headers=headers, params=querystring
                )
                data = response.text
                data = json.loads(data)
                try:
                    data_df.extend(data["data"])
                except KeyError:
                    print(data)
                    pass
                pbar.update(1)

        with tqdm(total=len(data_df)) as pbar:
            for item in data_df:
                m = Leagues(**item)
                m.save()
                pbar.update(1)

    # Update database
    def events_by_leagues(self, options):
        leagues = list(AtpTour.objects.filter(date__gte='2023-05-1').values_list('id'))
        wta_leagues = list(WtaTour.objects.filter(date__gte='2023-05-1').values_list('id'))
        ch_leagues = list(ChTour.objects.filter(date__gte='2023-05-1').values_list('id'))
        leagues = wta_leagues + leagues + ch_leagues

        for id in leagues:
            id = id[0].split('-')[1]
            #id = id[0]
            print(id)
            url = "https://sportscore1.p.rapidapi.com/leagues/"+id+"/events"

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
            try:
                data_df = data['data']
            except:
                continue
            meta_from = data['meta']["from"]
            current_page = data['meta']["current_page"]
            per_page = data['meta']["per_page"]
            meta_to = data['meta']["to"]

            if meta_to is not None:
                print('type',type(meta_to))
                print('meta_to', meta_to)
                print('per_page', per_page)
                print('type', type(per_page))
                while meta_to >= per_page:
                    current_page += 1
                    querystring = {"page": str(current_page)}
                    response = requests.request(
                        "GET", url, headers=headers, params=querystring
                    )
                    data = response.text
                    data = json.loads(data)
                    data_df.extend(data["data"])
                    per_page += data['meta']["per_page"]
                    meta_to = data['meta']["to"]
                    print('type', type(meta_to))
                    print('meta_to', meta_to)
                    print('per_page', per_page)
                    print('type', type(per_page))
                    if meta_to is None:
                        break

            with tqdm(total=len(data_df)) as pbar:
                for item in data_df:
                    print(item)
                    m = Events(**item)
                    m.save()
                    pbar.update(1)


    # FIX TO PAGE
    def list_events(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/events"
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
        to = data['meta']["to"]

        with tqdm(total=to) as pbar:
            for page in range(1, to+1000):
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
                m = Events(**item)
                m.save()
                pbar.update(1)

    def list_players(self, options):
        url = "https://sportscore1.p.rapidapi.com/players"
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
        print(data)
        data = json.loads(data)
        data_df = data['data']
        to = data['meta']["to"]
        #to = 10
        with tqdm(total=to) as pbar:
            for page in range(1, to+1):
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
                try:
                    m = Players(**item)
                except TypeError:
                    item['name_translations'] = item.pop('name_translation')
                    m = Players(**item)
                m.save()
                pbar.update(1)

    def event_players(self, options):
        qs = list(Events.objects.filter(sport_id=2).values_list('home_team_id', flat=True).distinct())
        qs2 = Events.objects.filter(sport_id=2).values_list('away_team_id', flat=True).distinct()

        in_first = set(qs)
        in_second = set(qs2)

        in_second_but_not_in_first = in_second - in_first

        result = qs + list(in_second_but_not_in_first)

        with tqdm(total=len(qs)) as pbar:
            for id in result[0:1]:
                url = "https://sportscore1.p.rapidapi.com/players/" + str(id)

                headers = {
                    "X-RapidAPI-Key": "a4d03aeecbmsh56ecc366e6cbecbp1d03c0jsn366ab7c0dc51",
                    "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
                }

                response = requests.request("GET", url, headers=headers)

                data = response.text
                data = json.loads(data)
                m = Players(**data["data"])
                m.save()

    def list_teams(self, options):
        url = "https://sportscore1.p.rapidapi.com/teams"
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
        print(data)
        data = json.loads(data)
        data_df = data['data']
        to = data['meta']["to"]
        current_page = data['meta']["current_page"]
        per_page = data['meta']["per_page"]
        meta_to = data['meta']["to"]
        if meta_to is not None:
            while meta_to >= per_page:
                current_page += 1
                querystring = {"page": str(current_page)}
                response = requests.request(
                    "GET", url, headers=headers, params=querystring
                )
                data = response.text
                data = json.loads(data)
                data_df.extend(data["data"])
                per_page += data['meta']["per_page"]
                meta_to = data['meta']["to"]
                if meta_to is None:
                    break

        with tqdm(total=len(data_df)) as pbar:
            for item in data_df:
                m = Teams(**item)
                m.save()
                pbar.update(1)

    def events_by_section_id(self, options):
        url = "https://sportscore1.p.rapidapi.com/sections/143/events"
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
        print(data)
        data = json.loads(data)
        data_df = data['data']
        to = data['meta']["to"]
        current_page = data['meta']["current_page"]
        per_page = data['meta']["per_page"]
        meta_to = data['meta']["to"]

        if meta_to is not None:
            while meta_to >= per_page:
                current_page += 1
                querystring = {"page": str(current_page)}
                response = requests.request(
                    "GET", url, headers=headers, params=querystring
                )
                data = response.text
                data = json.loads(data)
                data_df.extend(data["data"])
                per_page += data['meta']["per_page"]
                meta_to = data['meta']["to"]
                print('type', type(meta_to))
                print('meta_to', meta_to)
                print('per_page', per_page)
                print('type', type(per_page))
                if meta_to is None:
                    break

        with tqdm(total=len(data_df)) as pbar:
            for item in data_df:
                print(item)
                m = Events(**item)
                m.save()
                pbar.update(1)
