import json
import time
import logging
import requests
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm
from sportscore.models import FootballEvents, Teams, Players

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Football Data Fetcher"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        list_sections_cmd = subparsers.add_parser("sections")
        list_sections_cmd.set_defaults(subcommand=self.list_sections)

        list_leagues_cmd = subparsers.add_parser("leagues-by-section")
        list_leagues_cmd.set_defaults(subcommand=self.list_leagues_by_section_id)

        events_cmd = subparsers.add_parser("events")
        events_cmd.set_defaults(subcommand=self.football_events_by_leagues)

        teams_cmd = subparsers.add_parser("teams")
        teams_cmd.set_defaults(subcommand=self.list_teams)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def list_sections(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/1/sections"
        headers = {
            "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        querystring = {"page": "1"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        data_df = data['data']
        df = pd.DataFrame(data_df)
        logger.info(f"Football Sections:\n{df[['id', 'name', 'priority']]}")

    def list_leagues_by_section_id(self, options):
        url = 'https://sportscore1.p.rapidapi.com/sections/40/leagues'
        headers = {
            "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        data_df = data['data']
        columns = ['id', 'slug', 'start_date', 'priority', 'facts']
        df = pd.DataFrame(data_df)
        logger.info(f"Football Leagues:\n{df[columns]}")

    def football_events_by_leagues(self, options):
        football_leagues = [
            ['317', 'Premier League'],
            ['326', 'Championship'],
            ['318', 'FA Cup'],
            ['320', 'EFL Cup'],
            ['251', 'La Liga'],
            ['252', 'Cop Del Rey'],
            ['512', 'Bundesliga'],
            ['498', 'Ligue 1'],
            ['592', 'Serie A'],
            ['593', 'Coppa Italia'],
        ]

        for league_id in football_leagues:
            logger.info(f"League: {league_id[1]}")
            events_by_league_id = "https://sportscore1.p.rapidapi.com/leagues/" + league_id[0] + "/events"

            headers = {
                "X-RapidAPI-Key": settings.SPORT_SCORE_KEY,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            querystring = {"page": "1"}
            response = requests.request("GET", events_by_league_id, headers=headers, params=querystring)

            try:
                data = json.loads(response.text)
                data_df = data['data']
                meta_from = data['meta']["from"]
                current_page = data['meta']["current_page"]
                per_page = data['meta']["per_page"]
                meta_to = data['meta']["to"]

                if meta_to is not None:
                    while meta_to >= per_page:
                        current_page += 1
                        querystring = {"page": str(current_page)}
                        response = requests.request(
                            "GET", events_by_league_id, headers=headers, params=querystring
                        )
                        data = json.loads(response.text)
                        try:
                            data_df.extend(data["data"])
                        except json.JSONDecodeError as e:
                            logger.error(data)
                            continue
                        per_page += data['meta']["per_page"]
                        meta_to = data['meta']["to"]
                        if meta_to is None:
                            break

                with tqdm(total=len(data_df)) as pbar:
                    for item in data_df:
                        m = FootballEvents(**item)
                        m.save()
                        pbar.update(1)
            except (json.JSONDecodeError, KeyError):
                continue

    def list_teams(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/1/teams"
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
                m = Teams(**item)
                m.save()
                pbar.update(1)
