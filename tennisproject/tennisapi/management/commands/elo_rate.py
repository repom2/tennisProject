from django.core.management.base import BaseCommand
from tennisapi.elo_ratings.atp_elo import atp_elorate


class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        atp_elo_cmd = subparsers.add_parser("atp")
        atp_elo_cmd.set_defaults(subcommand=self.atp_elo)
        atp_elo_cmd.add_argument("surface", type=str)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def atp_elo(self, options):
        surface = options["surface"]
        atp_elorate(surface)
