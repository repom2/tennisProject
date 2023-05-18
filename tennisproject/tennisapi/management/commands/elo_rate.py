from django.core.management.base import BaseCommand
from tennisapi.elo_ratings.atp_elo import atp_elorate
from tennisapi.elo_ratings.wta_elo import wta_elorate
from tennisapi.elo_ratings.ch_elo import ch_elorate


class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        atp_elo_cmd = subparsers.add_parser("atp")
        atp_elo_cmd.set_defaults(subcommand=self.atp_elo)
        atp_elo_cmd.add_argument("surface", type=str)

        ch_elo_cmd = subparsers.add_parser("ch")
        ch_elo_cmd.set_defaults(subcommand=self.ch_elo)
        ch_elo_cmd.add_argument("surface", type=str)

        wta_elo_cmd = subparsers.add_parser("wta")
        wta_elo_cmd.set_defaults(subcommand=self.wta_elo)
        wta_elo_cmd.add_argument("surface", type=str)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def atp_elo(self, options):
        surface = options["surface"]
        atp_elorate(surface)

    def wta_elo(self, options):
        surface = options["surface"]
        wta_elorate(surface)

    def ch_elo(self, options):
        surface = options["surface"]
        ch_elorate(surface)
