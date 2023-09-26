from django.core.management.base import BaseCommand
from tennisapi.stats.serve_return import serve_points
from tennisapi.stats.fatigue_modelling import fatigue_modelling
from tennisapi.stats.head2head import head2head
from tennisapi.stats.surface_weighting.sipko_surface_weighting import surface_weighting
from tennisapi.stats.prob_by_serve.winning_match import matchProb
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from psycopg2.extensions import AsIs


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

    def handle(self, *args, **options):
        options["subcommand"](options)

    def serve_stats(self, options):
        serve_points()

    def surface_correlation(self, options):
        surface_weighting()

    def player_fatigue(self, options):
        fatigue_modelling()

    def head_to_head(self, options):
        head2head()

    def match_prob(self, options):
        tour_table = 'tennisapi_atptour'
        matches_table = 'tennisapi_atpmatches'
        event = 'nur%%sult'
        date = '2018-1-1'
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
