from django.core.management.base import BaseCommand
from footballapi.elo_ratings.premier_elo import premier_elorate
from footballapi.elo_ratings.championship_elo import championship_elorate


class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        premier_cmd = subparsers.add_parser("premier")
        premier_cmd.set_defaults(subcommand=self.premier)

        championship_cmd = subparsers.add_parser("championship")
        championship_cmd.set_defaults(subcommand=self.championship)


    def handle(self, *args, **options):
        options["subcommand"](options)

    def premier(self, options):
        premier_elorate()

    def championship(self, options):
        championship_elorate()
