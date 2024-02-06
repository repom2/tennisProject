from django.core.management.base import BaseCommand
from icehockeyapi.elo_ratings.liiga_elo import liiga_elorate
from icehockeyapi.elo_ratings.liiga_elo_home import liiga_elo_home


class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        liiga_cmd = subparsers.add_parser("liiga")
        liiga_cmd.set_defaults(subcommand=self.liiga)

        liiga_home_cmd = subparsers.add_parser("liiga-home")
        liiga_home_cmd.set_defaults(subcommand=self.liiga_home)


    def handle(self, *args, **options):
        options["subcommand"](options)

    def liiga(self, options):
        liiga_elorate()

    def liiga_home(self, options):
        liiga_elo_home()
