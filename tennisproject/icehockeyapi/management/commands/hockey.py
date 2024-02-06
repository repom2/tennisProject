from django.core.management.base import BaseCommand
from icehockeyapi.ml.predict import predict


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        predict_matches_cmd = subparsers.add_parser("pred")
        predict_matches_cmd.set_defaults(subcommand=self.predict_matches)
        predict_matches_cmd.add_argument("pred", type=str, default='liiga')


    def handle(self, *args, **options):
        options["subcommand"](options)

    def predict_matches(self, options):
        level = options["pred"]
        predict(level)


