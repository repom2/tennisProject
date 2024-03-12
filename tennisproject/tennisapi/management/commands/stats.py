from django.core.management.base import BaseCommand
from tennisapi.stats.serve_return import serve_points
from tennisapi.stats.fatigue_modelling import fatigue_modelling
from tennisapi.stats.head2head import head2head
from tennisapi.stats.surface_weighting.sipko_surface_weighting import surface_weighting
from tennisapi.stats.prob_by_serve.winning_match import matchProb
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from tennisapi.stats.common_opponent import common_opponent
from psycopg2.extensions import AsIs
from tennisapi.scrape.wta_site import wta_scrape
from tennisapi.scrape.tennisabstract_site import tennisabstract_scrape


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        serve_cmd = subparsers.add_parser("serve")
        serve_cmd.set_defaults(subcommand=self.serve_stats)

        surf_corr_cmd = subparsers.add_parser("surf-corr")
        surf_corr_cmd.set_defaults(subcommand=self.surface_correlation)

        fatigue_cmd = subparsers.add_parser("fatigue")
        fatigue_cmd.set_defaults(subcommand=self.player_fatigue)

        head_cmd = subparsers.add_parser("head")
        head_cmd.set_defaults(subcommand=self.head_to_head)

        match_prob_cmd = subparsers.add_parser("match-prob")
        match_prob_cmd.set_defaults(subcommand=self.match_prob)

        common_opponent_cmd = subparsers.add_parser("common-opponent")
        common_opponent_cmd.set_defaults(subcommand=self.commonn_opponent_stats)

        scrape_cmd = subparsers.add_parser("scrape")
        scrape_cmd.set_defaults(subcommand=self.scrape_stats)

        scrape_cmd = subparsers.add_parser("ta")
        scrape_cmd.set_defaults(subcommand=self.tennisabstract_stats)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def serve_stats(self, options):
        serve_points()

    def scrape_stats(self, options):
        wta_scrape()

    def tennisabstract_stats(self, options):
        tennisabstract_scrape()

    def surface_correlation(self, options):
        surface_weighting()

    def player_fatigue(self, options):
        fatigue_modelling()

    def head_to_head(self, options):
        head2head()

    def match_prob(self, options):
        tour_table = 'tennisapi_atptour'
        tour_table = 'tennisapi_wtatour'
        matches_table = 'tennisapi_wtamatches'
        event = 'nur%%sult'
        date = '2010-1-1'
        params = {
            'event': AsIs(event),
            'tour_table': AsIs(tour_table),
            'matches_table': AsIs(matches_table),
            'date': date,
        }
        event_spw, event_rpw = event_stats(params)
        params['event'] = AsIs('')
        tour_spw, tour_rpw = event_stats(params)
        print('event', event_spw, event_rpw)
        print('tour', tour_spw, tour_rpw)
        player1_spw = 0.6799
        player1_rpw = 0.3478
        player2_spw = 0.6461
        player2_rpw = 0.3795
        player1 = event_spw + (player1_spw - tour_spw) - (player2_rpw - tour_rpw)
        player2 = event_spw + (player2_spw - tour_spw) - (player1_rpw - tour_rpw)
        print(player1, player2)
        win = matchProb(player1, 1-player2, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3)
        print(win)

    def commonn_opponent_stats(self, options):
        tour_table = 'tennisapi_wtatour'
        matches_table = 'tennisapi_wtamatches'
        date = '2022-1-1'
        player1 = 'd9e7a540b10d3c355d7753b595a4daee'
        player2 = 'c6e64405c62f77042e7287ab19c923ab'
        params = {
            'tour_table': AsIs(tour_table),
            'matches_table': AsIs(matches_table),
        }
        event_spw = 0.57
        stats = common_opponent(params, player1, player2, event_spw, date)
        print(stats)

        data = matchProb(
                stats[0] if stats[0] else 0.55,
                1 - stats[1] if stats[1] else 0.55,
                gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3
            )
        print(data)
