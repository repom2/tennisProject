from django.core.management.base import BaseCommand
from tennisapi.ml.rolandgarros import tennis_prediction
from tennisapi.ml.rolandgarros_pred import predict_matches


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        roland_cmd = subparsers.add_parser("roland")
        roland_cmd.set_defaults(subcommand=self.roland)

        roland_pred_cmd = subparsers.add_parser("roland-pred")
        roland_pred_cmd.set_defaults(subcommand=self.roland_predict)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def roland(self, options):
        tennis_prediction()

    def roland_predict(self, options):
        predict_matches()
