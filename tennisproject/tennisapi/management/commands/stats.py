from django.core.management.base import BaseCommand
from tennisapi.stats.serve_return import serve_points
from tennisapi.stats.fatigue_modelling import fatigue_modelling
from tennisapi.stats.head2head import head2head
from tennisapi.stats.surface_weighting.sipko_surface_weighting import surface_weighting


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
