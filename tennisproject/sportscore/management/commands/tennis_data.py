import json
import time
import logging
import requests
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from tqdm import tqdm
from sportscore.models import TennisTournaments, TennisEvents, Teams, Stats
from .match_statistics import MatchStatisticsFetcher

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Tennis Data Fetcher"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        list_sections_cmd = subparsers.add_parser("sections")
        list_sections_cmd.set_defaults(subcommand=self.list_sections)

        tournaments_cmd = subparsers.add_parser("tournaments")
        tournaments_cmd.set_defaults(subcommand=self.list_tennis_tournaments)

        events_cmd = subparsers.add_parser("events")
        events_cmd.set_defaults(subcommand=self.tennis_events_by_sections)

        players_cmd = subparsers.add_parser("players")
        players_cmd.set_defaults(subcommand=self.tennis_players)

        stats_cmd = subparsers.add_parser("stats")
        stats_cmd.set_defaults(subcommand=self.tennis_match_statistics)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def list_sections(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/sections"
        headers = {
            "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        querystring = {"page": "1"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        data_df = data['data']
        df = pd.DataFrame(data_df)
        logger.info(f"Tennis Sections:\n{df[['id', 'name', 'priority']]}")

    def list_tennis_tournaments(self, options):
        section_ids = [
            '145',  # ATP
            '144',  # WTA
        ]
        
        for section_id in section_ids:
            url = f"https://sportscore1.p.rapidapi.com/sections/{section_id}/leagues"
            headers = {
                "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers)
            data = json.loads(response.text)
            data_df = data['data']
            last_page = data['meta']["last_page"]

            with tqdm(total=last_page) as pbar:
                for page in range(2, last_page + 1):
                    querystring = {"page": str(page)}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    data = json.loads(response.text)
                    try:
                        data_df.extend(data["data"])
                    except KeyError:
                        logger.error(f"Error in page {page}")
                        pass
                    pbar.update(1)
                    time.sleep(1)

            with tqdm(total=len(data_df)) as pbar:
                for item in data_df:
                    m = TennisTournaments(**item)
                    try:
                        m.save()
                    except ValidationError:
                        logger.error(f"Validation error for tournament {item.get('id')}")
                    pbar.update(1)

    def tennis_events_by_sections(self, options):
        tennis_sections = [
            '145',  # ATP
            '144',  # WTA
        ]

        for section_id in tennis_sections:
            events_url = f"https://sportscore1.p.rapidapi.com/sections/{section_id}/events"
            headers = {
                "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            querystring = {"page": "1"}
            response = requests.request("GET", events_url, headers=headers, params=querystring)
            
            try:
                data = json.loads(response.text)
                data_df = data['data']
                current_page = data['meta']["current_page"]
                per_page = data['meta']["per_page"]
                meta_to = data['meta']["to"]

                if meta_to is not None:
                    while meta_to >= per_page:
                        current_page += 1
                        querystring = {"page": str(current_page)}
                        response = requests.request("GET", events_url, headers=headers, params=querystring)
                        data = json.loads(response.text)
                        try:
                            data_df.extend(data["data"])
                        except (json.JSONDecodeError, KeyError):
                            continue
                        per_page += data['meta']["per_page"]
                        meta_to = data['meta']["to"]
                        if meta_to is None:
                            break

                with tqdm(total=len(data_df)) as pbar:
                    for item in data_df:
                        m = TennisEvents(**item)
                        m.save()
                        pbar.update(1)
            except (json.JSONDecodeError, KeyError):
                continue

    def tennis_players(self, options):
        # In tennis, players are treated as teams in the API
        url = "https://sportscore1.p.rapidapi.com/sports/2/teams"
        headers = {
            "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        querystring = {"page": "1"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        data_df = data['data']
        current_page = data['meta']["current_page"]
        per_page = data['meta']["per_page"]
        meta_to = data['meta']["to"]
        
        if meta_to is not None:
            while meta_to >= per_page:
                current_page += 1
                querystring = {"page": str(current_page)}
                response = requests.request("GET", url, headers=headers, params=querystring)
                data = json.loads(response.text)
                try:
                    data_df.extend(data["data"])
                except KeyError:
                    logger.error("No data in response")
                    continue
                per_page += data['meta']["per_page"]
                meta_to = data['meta']["to"]
                if meta_to is None:
                    break

        with tqdm(total=len(data_df)) as pbar:
            for item in data_df:
                # In tennis API, players are represented as teams
                m = Teams(**item)
                m.save()
                pbar.update(1)

    def tennis_match_statistics(self, options):
        fetcher = MatchStatisticsFetcher(settings.SPORT_SCORE_KEY)
        fetcher.match_statistics({})
