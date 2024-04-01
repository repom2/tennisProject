import json
import os
import time
import pandas as pd
import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from sportscore.models import TennisTournaments, Leagues, Events, Players, Teams, Stats, FootballEvents, IceHockeyEvents, TennisEvents
from tennisapi.models import AtpMatches, ChTour, WtaMatches
from tennisapi.models import Match, WtaMatch, AtpTour, WtaTour
from tqdm import tqdm
from django.conf import settings
import logging
from tabulate import tabulate
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

pd.set_option('display.max_columns', None)

sport_score_key = settings.SPORT_SCORE_KEY


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

        list_league_by_section_cmd = subparsers.add_parser("leagues-by-section")
        list_league_by_section_cmd.set_defaults(subcommand=self.list_leagues_by_section_id)

        list_tennis_tournaments_cmd = subparsers.add_parser("tennis-tournaments")
        list_tennis_tournaments_cmd.set_defaults(subcommand=self.list_tennis_tournaments)

        list_leagues_cmd = subparsers.add_parser("leagues")
        list_leagues_cmd.set_defaults(subcommand=self.list_leagues)

        events_by_leagues_cmd = subparsers.add_parser("events-by-leagues")
        events_by_leagues_cmd.set_defaults(subcommand=self.events_by_leagues)

        football_events_by_leagues_cmd = subparsers.add_parser("football-events-by-leagues")
        football_events_by_leagues_cmd.set_defaults(subcommand=self.football_events_by_leagues)

        tennis_events_by_sections_cmd = subparsers.add_parser(
            "tennis-events-by-sections")
        tennis_events_by_sections_cmd.set_defaults(
            subcommand=self.tennis_events_by_sections)

        hockey_events_by_leagues_cmd = subparsers.add_parser(
            "ice-hockey-events-by-leagues")
        hockey_events_by_leagues_cmd.set_defaults(
            subcommand=self.ice_hockey_events_by_leagues)

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

        stats_cmd = subparsers.add_parser("stats")
        stats_cmd.set_defaults(subcommand=self.match_statistics)

        tennis_stats_cmd = subparsers.add_parser("tennis-stats")
        tennis_stats_cmd.set_defaults(subcommand=self.tennis_api_match_statistics)

    def handle(self, *args, **options):
        options["subcommand"](options)

    # NO NEED
    def list_sports(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports"
        sport_score_key = settings.SPORT_SCORE_KEY
        headers = {
            "X-RapidAPI-Key": sport_score_key,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)

        data = response.text
        data = json.loads(data)
        data_df = data['data']
        df = pd.DataFrame(data_df)
        logging.info(
            f"DataFrame:\n{tabulate(df[['id', 'slug']], headers='keys', tablefmt='psql', showindex=False)}")

    # SECTION ID
    def list_sections(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/sections"
        headers = {
            "X-RapidAPI-Key": sport_score_key,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        querystring = {"page": "1"}

        response = requests.request(
            "GET", url, headers=headers, params=querystring
        )

        data = response.text
        data = json.loads(data)
        data_df = data['data']
        df = pd.DataFrame(data_df)
        # sort by priority field
        #df = df.sort_values(by='priority', ascending=False)
        columns = ['id', 'name', 'priority']
        logging.info(
            f"DataFrame:\n{tabulate(df, headers='keys', tablefmt='psql', showindex=False)}")
        logging.info(data["meta"])

    def list_leagues_by_section_id(self, options):
        url =  'https://sportscore1.p.rapidapi.com/sections/40/leagues'

        headers = {
            "X-RapidAPI-Key": sport_score_key,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        response = requests.request(
            "GET", url, headers=headers)

        data = response.text
        data = json.loads(data)
        data_df = data['data']
        columns = ['id', 'slug', 'start_date', 'priority', 'facts']
        df = pd.DataFrame(data_df)
        logging.info(
            f"DataFrame:\n{tabulate(df[columns], headers='keys', tablefmt='psql', showindex=False)}")


    def list_leagues(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/leagues"
        headers = {
            "X-RapidAPI-Key": sport_score_key,
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
                time.sleep(1)

        with tqdm(total=len(data_df)) as pbar:
            for item in data_df:
                m = Leagues(**item)
                m.save()
                pbar.update(1)


    # Update database
    def events_by_leagues(self, options):
        #leagues = list(Match.objects.filter(start_at__gte='2024-3-10').values_list('tour_id').distinct('tour_id'))
        #wta_leagues = list(WtaMatch.objects.filter(start_at__gte='2024-3-10').values_list('tour_id').distinct('tour_id'))
        #leagues = wta_leagues + leagues #+ ch_leagues
        # Make queryset text field to date time now
        date_now = datetime.now() - timedelta(days=14)
        leagues = TennisTournaments.objects.filter(start_date__gte=date_now).values_list('id', 'slug')
        #ch_leagues = list(ChTour.objects.filter(date__gte='2023-06-15').values_list('id'))

        logging.info(f"Leagues: {len(leagues)}")
        sport_score_key = settings.SPORT_SCORE_KEY
        #leagues = [('6945',)]
        for id in leagues:
            logging.info(f"League: {id}")
            id = str(id[0])
            url = "https://sportscore1.p.rapidapi.com/leagues/"+id+"/events"

            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            querystring = {"page": "1"}

            response = requests.request(
                "GET", url, headers=headers, params=querystring
            )

            data = response.text

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                continue
            try:
                data_df = data['data']
            except:
                continue
            meta_from = data['meta']["from"]
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
                    try:
                        data_df.extend(data["data"])
                    except json.JSONDecodeError:
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

    # Update database
    def football_events_by_leagues(self, options):
        football_leagues = [
            ['317', 'Premier League'],
            ['326', 'Championship'],
            ['326', 'FA Cup'],
            ['251', 'La Liga'],
            ['512', 'Bundesliga'],
            ['498', 'Ligue 1'],
            ['592', 'Serie A']
        ]

        for league_id in football_leagues:
            logging.info(f"League: {league_id[1]}")
            events_by_league_id = "https://sportscore1.p.rapidapi.com/leagues/" + league_id[0] + "/events"

            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            querystring = {"page": "1"}

            response = requests.request(
                "GET", events_by_league_id, headers=headers, params=querystring
            )

            data = response.text

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                continue
            try:
                data_df = data['data']
            except:
                continue
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
                    data = response.text
                    data = json.loads(data)
                    try:
                        data_df.extend(data["data"])
                    except json.JSONDecodeError as e:
                        logging.error(data)
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

    def ice_hockey_events_by_leagues(self, options):
        ice_hockey_leagues = ['7622'] # mestis 7623

        for league_id in ice_hockey_leagues:
            events_by_league_id = "https://sportscore1.p.rapidapi.com/leagues/" + league_id + "/events"

            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            querystring = {"page": "1"}

            response = requests.request(
                "GET", events_by_league_id, headers=headers, params=querystring
            )

            data = response.text

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                continue
            try:
                data_df = data['data']
            except:
                continue
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
                    data = response.text
                    data = json.loads(data)
                    try:
                        data_df.extend(data["data"])
                    except json.JSONDecodeError:
                        continue
                    per_page += data['meta']["per_page"]
                    meta_to = data['meta']["to"]
                    if meta_to is None:
                        break

            with tqdm(total=len(data_df)) as pbar:
                for item in data_df:
                    m = IceHockeyEvents(**item)
                    m.save()
                    pbar.update(1)


    def tennis_events_by_sections(self, options):
        tennis_sections = [
            '145', # ATP
            '144', # WTA
            #'143', # Challenger
            #'142', # Challenger-women
            #'141', # ITF
            #'139', # Davis Cup
            #'138', # Fed Cup
        ]

        for section_id in tennis_sections:
            events_by_league_id = "https://sportscore1.p.rapidapi.com/sections/" + section_id + "/events"

            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            querystring = {"page": "1"}

            response = requests.request(
                "GET", events_by_league_id, headers=headers, params=querystring
            )

            data = response.text

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                continue
            try:
                data_df = data['data']
            except:
                continue
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
                    data = response.text
                    data = json.loads(data)
                    try:
                        data_df.extend(data["data"])
                    except (json.JSONDecodeError, KeyError) as e:
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

    # FIX TO PAGE
    def list_events(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/events"
        sport_score_key = settings.SPORT_SCORE_KEY
        headers = {
            "X-RapidAPI-Key": sport_score_key,
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
        sport_score_key = settings.SPORT_SCORE_KEY
        headers = {
            "X-RapidAPI-Key": sport_score_key,
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
        sport_score_key = settings.SPORT_SCORE_KEY
        with tqdm(total=len(qs)) as pbar:
            for id in result[0:1]:
                url = "https://sportscore1.p.rapidapi.com/players/" + str(id)

                headers = {
                    "X-RapidAPI-Key": sport_score_key,
                    "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
                }

                response = requests.request("GET", url, headers=headers)

                data = response.text
                data = json.loads(data)
                m = Players(**data["data"])
                m.save()

    def list_teams(self, options):
        url = "https://sportscore1.p.rapidapi.com/sports/2/teams"
        sport_score_key = settings.SPORT_SCORE_KEY
        headers = {
            "X-RapidAPI-Key": sport_score_key,
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
                try:
                    data_df.extend(data["data"])
                except KeyError:
                    logging.error("No per_page in data")
                    logging.error(data)
                    continue
                try:
                    per_page += data['meta']["per_page"]
                except KeyError:
                    logging.error("No per_page in data")
                    logging.error(data)
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
        sport_score_key = settings.SPORT_SCORE_KEY
        headers = {
            "X-RapidAPI-Key": sport_score_key,
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
                print(item)
                m = Events(**item)
                m.save()
                pbar.update(1)


    def match_statistics(self, options):
        sportscore_ids = list(
            AtpMatches.objects.filter(Q(date__gt='2024-3-1') & Q(w_ace__isnull=True)).values_list('event_id')
        )
        sportscore_wta_ids = list(
            WtaMatches.objects.filter(
                Q(date__gt='2024-3-1') & Q(w_ace__isnull=True)).values_list(
                'event_id')
        )

        sportscore_ids += sportscore_wta_ids

        logging.info("Total ids to fetch: " + str(len(sportscore_ids)))

        def fetch_date(id):
            sport_score_key = settings.SPORT_SCORE_KEY
            url = "https://sportscore1.p.rapidapi.com/events/" + str(id) + "/statistics"

            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            response = requests.request(
                "GET", url, headers=headers,
            )

            data = response.text

            return data

        with tqdm(total=len(sportscore_ids)) as pbar:
            for id in sportscore_ids:
                id = id[0]
                data = fetch_date(id)
                if "rate limit per second" in data:
                    time.sleep(0.5)
                    data = fetch_date(id)
                if "rate limit per second" in data:
                    time.sleep(0.5)
                    data = fetch_date(id)
                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError:
                    continue
                m = Stats(id=id, data=data)
                m.save()
                pbar.update(1)


    def tennis_api_match_statistics(self, options):
        sportscore_ids = list(
            AtpMatch.objects.filter(Q(start_at__gte='2024-02-02') &  Q(w_ace__isnull=True)).values_list('event_id')
        )

        sportscore_ids += list(
            WtaMatch.objects.filter(Q(start_at__gte='2024-02-02') & Q(w_ace__isnull=True)).values_list('event_id')
        )

        def fetch_date(id):
            sport_score_key = settings.SPORT_SCORE_KEY
            url = "https://sportscore1.p.rapidapi.com/events/" + str(id) + "/statistics"

            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            response = requests.request(
                "GET", url, headers=headers,
            )

            data = response.text

            return data

        with tqdm(total=len(sportscore_ids)) as pbar:
            for id in sportscore_ids:
                id = id[0]
                data = fetch_date(id)
                if "rate limit per second" in data:
                    time.sleep(0.5)
                    data = fetch_date(id)
                if "rate limit per second" in data:
                    time.sleep(0.5)
                    data = fetch_date(id)
                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError:
                    continue
                m = Stats(id=id, data=data)
                m.save()
                pbar.update(1)


    # Tennis tournaments by section id
    def list_tennis_tournaments(self, options):
        section_ids =  [
            '145', # ATP
            #'143', # Challenger
            #'137', # Grand Slam
            #'139', # Davis Cup
            #'142', # Challenger women
            #'141', # Itf Women
            '144', # WTA
            #'138', # Federation Cup women
            ]
        for section_id in section_ids:
            url = f"https://sportscore1.p.rapidapi.com/sections/{section_id}/leagues"
            headers = {
                "X-RapidAPI-Key": sport_score_key,
                "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
            }

            response = requests.request(
                "GET", url, headers=headers)

            data = response.text
            data = json.loads(data)
            data_df = data['data']
            #logging.info(data_df[0])

            last_page = data['meta']["last_page"]

            with tqdm(total=last_page) as pbar:
                for page in range(2, last_page + 1):
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
                    time.sleep(1)

            with tqdm(total=len(data_df)) as pbar:
                for item in data_df:
                    m = TennisTournaments(**item)
                    m.save()
                    pbar.update(1)
