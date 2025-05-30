import pandas as pd
import json
import os
import numpy as np
from django.conf import settings

import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from tennis_atp.models import WTAPlayers, WtaMatches
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

        list_wta_matches_cmd = subparsers.add_parser("matches")
        list_wta_matches_cmd.set_defaults(subcommand=self.list_wta_matches)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def list_players(self, options):
        file_name = "/app/tennis_atp/wta_data/tennis_wta/wta_players.csv"
        tmp_data = pd.read_csv(file_name, sep=',')
        products = [
            WTAPlayers(
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
        WTAPlayers.objects.bulk_create(products)

    def list_wta_matches(self, options):
        start_year = 1968
        end_year = 2023
        for i in range(start_year, end_year + 1):
            file_name = "/app/tennis_atp/wta_data/tennis_wta/wta_matches_" + str(i) + ".csv"
            tmp_data = pd.read_csv(file_name, sep=',')
            tmp_data = tmp_data.replace(np.nan, None)
            matches = [
                WtaMatches(
                    tourney_id=row['tourney_id'],
                    tourney_name=row['tourney_name'],
                    surface=row['surface'],
                    draw_size=row['draw_size'],
                    tourney_level=row['tourney_level'],
                    tourney_date=row['tourney_date'],
                    match_num=row['match_num'],
                    winner_id=row['winner_id'],
                    winner_seed=row['winner_seed'],
                    winner_entry=row['winner_entry'],
                    winner_name=row['winner_name'],
                    winner_hand=row['winner_hand'],
                    winner_ht=row['winner_ht'],
                    winner_ioc=row['winner_ioc'],
                    winner_age=row['winner_age'],
                    loser_id=row['loser_id'],
                    loser_seed=row['loser_seed'],
                    loser_entry=row['loser_entry'],
                    loser_name=row['loser_name'],
                    loser_hand=row['loser_hand'],
                    loser_ht=row['loser_ht'],
                    loser_ioc=row['loser_ioc'],
                    loser_age=row['loser_age'],
                    score=row['score'],
                    best_of=row['best_of'],
                    round=row['round'],
                    minutes=row['minutes'],
                    w_ace=row['w_ace'],
                    w_df=row['w_df'],
                    w_svpt=row['w_svpt'],
                    w_firstin=row['w_1stIn'],
                    w_firstwon=row['w_1stWon'],
                    w_secondwon=row['w_2ndWon'],
                    w_svgms=row['w_SvGms'],
                    w_bpsaved=row['w_bpSaved'],
                    w_bpfaced=row['w_bpFaced'],
                    l_ace=row['l_ace'],
                    l_df=row['l_df'],
                    l_svpt=row['l_svpt'],
                    l_firstin=row['l_1stIn'],
                    l_firstwon=row['l_1stWon'],
                    l_secondwon=row['l_2ndWon'],
                    l_svgms=row['l_SvGms'],
                    l_bpsaved=row['l_bpSaved'],
                    l_bpfaced=row['l_bpFaced'],
                    winner_rank=row['winner_rank'],
                    winner_rank_points=row['winner_rank_points'],
                    loser_rank=row['loser_rank'],
                    loser_rank_points=row['loser_rank_points'],
                )
                for index, row in tmp_data.iterrows()
            ]
            WtaMatches.objects.bulk_create(matches)
