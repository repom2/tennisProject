from django.core.management.base import BaseCommand
from tennisapi.ml.rolandgarros import tennis_prediction
from tennisapi.ml.rolandgarros_wta import tennis_prediction_wta
from tennisapi.ml.rolandgarros_pred import predict_matches
from tennisapi.ml.rolandgarros_pred_wta import predict_matches_wta


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        roland_cmd = subparsers.add_parser("roland")
        roland_cmd.set_defaults(subcommand=self.roland)

        roland_wta_cmd = subparsers.add_parser("roland-wta")
        roland_wta_cmd.set_defaults(subcommand=self.roland_wta)

        roland_pred_cmd = subparsers.add_parser("roland-pred")
        roland_pred_cmd.set_defaults(subcommand=self.roland_predict)

        roland_pred_wta_cmd = subparsers.add_parser("roland-pred-wta")
        roland_pred_wta_cmd.set_defaults(subcommand=self.roland_predict_wta)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def roland(self, options):
        tennis_prediction()

    def roland_wta(self, options):
        tennis_prediction_wta()

    def roland_predict(self, options):
        predict_matches()

    def roland_predict_wta(self, options):
        predict_matches_wta()
