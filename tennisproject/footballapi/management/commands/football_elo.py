from django.core.management.base import BaseCommand
from footballapi.elo_ratings.premier_elo import premier_elorate
from footballapi.elo_ratings.championship_elo import championship_elorate
from footballapi.elo_ratings.premier_elo_home import premier_elo_home
from footballapi.elo_ratings.championship_elo_home import championship_elo_home
from footballapi.elo_ratings.laliga_elo import laliga_elorate
from footballapi.elo_ratings.laliga_elo_home import laliga_elo_home
from footballapi.elo_ratings.seriea_elo import seriea_elorate
from footballapi.elo_ratings.seriea_elo_home import seriea_elo_home
from footballapi.elo_ratings.bundesliga_elo import bundesliga_elorate
from footballapi.elo_ratings.bundesliga_elo_home import bundesliga_elo_home
from footballapi.elo_ratings.ligue1_elo import ligue1_elorate
from footballapi.elo_ratings.ligue1_elo_home import ligue1_elo_home
from icehockeyapi.elo_ratings.liiga_elo import liiga_elorate
from icehockeyapi.elo_ratings.liiga_elo_home import liiga_elo_home
from icehockeyapi.elo_ratings.mestis_elo import mestis_elorate
from icehockeyapi.elo_ratings.mestis_elo_home import mestis_elo_home

class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        all_cmd = subparsers.add_parser("all")
        all_cmd.set_defaults(subcommand=self.elo_run_all)

        premier_cmd = subparsers.add_parser("premier")
        premier_cmd.set_defaults(subcommand=self.premier)

        premier_home_cmd = subparsers.add_parser("premier-home")
        premier_home_cmd.set_defaults(subcommand=self.premier_home)

        championship_cmd = subparsers.add_parser("championship")
        championship_cmd.set_defaults(subcommand=self.championship)

        championship_home_cmd = subparsers.add_parser("championship-home")
        championship_home_cmd.set_defaults(subcommand=self.championship_home)

        laliga_cmd = subparsers.add_parser("laliga")
        laliga_cmd.set_defaults(subcommand=self.laliga)

        laliga_home_cmd = subparsers.add_parser("laliga-home")
        laliga_home_cmd.set_defaults(subcommand=self.laliga_home)

        seriea_cmd = subparsers.add_parser("seriea")
        seriea_cmd.set_defaults(subcommand=self.seriea)

        seriea_home_cmd = subparsers.add_parser("seriea-home")
        seriea_home_cmd.set_defaults(subcommand=self.seriea_home)

        bundesliga_cmd = subparsers.add_parser("bundesliga")
        bundesliga_cmd.set_defaults(subcommand=self.bundesliga)

        bundesliga_home_cmd = subparsers.add_parser("bundesliga-home")
        bundesliga_home_cmd.set_defaults(subcommand=self.bundesliga_home)

        ligue1_cmd = subparsers.add_parser("ligue1")
        ligue1_cmd.set_defaults(subcommand=self.ligue1)

        ligue1_home_cmd = subparsers.add_parser("ligue1-home")
        ligue1_home_cmd.set_defaults(subcommand=self.ligue1_home)


    def handle(self, *args, **options):
        options["subcommand"](options)

    def elo_run_all(self, options):
        premier_elorate()
        premier_elo_home()
        championship_elorate()
        championship_elo_home()
        laliga_elorate()
        laliga_elo_home()
        seriea_elorate()
        seriea_elo_home()
        bundesliga_elorate()
        bundesliga_elo_home()
        ligue1_elorate()
        ligue1_elo_home()
        liiga_elorate()
        liiga_elo_home()
        mestis_elorate()
        mestis_elo_home()

    def premier(self, options):
        premier_elorate()

    def premier_home(self, options):
        premier_elo_home()

    def championship(self, options):
        championship_elorate()

    def championship_home(self, options):
        championship_elo_home()

    def laliga(self, options):
        laliga_elorate()

    def laliga_home(self, options):
        laliga_elo_home()

    def seriea(self, options):
        seriea_elorate()

    def seriea_home(self, options):
        seriea_elo_home()

    def bundesliga(self, options):
        bundesliga_elorate()

    def bundesliga_home(self, options):
        bundesliga_elo_home()

    def ligue1(self, options):
        ligue1_elorate()

    def ligue1_home(self, options):
        ligue1_elo_home()
