from django.core.management.base import BaseCommand
from tennisapi.ml.rolandgarros import tennis_prediction
from tennisapi.ml.stuttgart_hertogenbosch import tennis_prediction as grass_prediction
from tennisapi.ml.stuttgart_herto_wta import tennis_prediction as wta_grass_prediction
from tennisapi.ml.rolandgarros_wta import tennis_prediction_wta
from tennisapi.ml.wimbledon import wimbledon
from tennisapi.ml.wimbledon_wta import wimbledon_wta
from tennisapi.ml.wimbledon_wta import wimbledon_wta
from tennisapi.ml.wimbledon_wta_pred import wimbledon_pred_wta
from tennisapi.ml.rolandgarros_pred import predict_matches
from tennisapi.ml.stuttgart_hertogenbosch_pred \
    import predict_matches as predict_stutt_herto_matches
from tennisapi.ml.stuttgart_herto_wta_pred \
    import predict_matches as predict_stutt_herto_wta_matches
from tennisapi.ml.rolandgarros_pred_history import predict_matches_history
from tennisapi.ml.rolandgarros_pred_wta import predict_matches_wta
from tennisapi.ml.rolandgarros_pred_wta_history import predict_matches_wta_history
from tennisapi.ml.model_interact import feature_importance


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        roland_cmd = subparsers.add_parser("roland")
        roland_cmd.set_defaults(subcommand=self.roland)

        wimbledon_cmd = subparsers.add_parser("wimbledon")
        wimbledon_cmd.set_defaults(subcommand=self.wimbledon_atp)

        wimbledon_wta_cmd = subparsers.add_parser("wimbledon-wta")
        wimbledon_wta_cmd.set_defaults(subcommand=self.wimbledon_wta_model)

        wimbledon_pred_cmd = subparsers.add_parser("wimbledon-pred")
        wimbledon_pred_cmd.set_defaults(subcommand=self.wimbledon_predict)

        wimbledon_pred_wta_cmd = subparsers.add_parser("wimbledon-pred-wta")
        wimbledon_pred_wta_cmd.set_defaults(subcommand=self.wimbledon_predict_wta)

        stutt_herto_cmd = subparsers.add_parser("stutt-herto")
        stutt_herto_cmd.set_defaults(subcommand=self.stutt_herto)

        stutt_herto_wta_cmd = subparsers.add_parser("stutt-herto-wta")
        stutt_herto_wta_cmd.set_defaults(subcommand=self.stutt_herto_wta)

        roland_wta_cmd = subparsers.add_parser("roland-wta")
        roland_wta_cmd.set_defaults(subcommand=self.roland_wta)

        roland_pred_cmd = subparsers.add_parser("roland-pred")
        roland_pred_cmd.set_defaults(subcommand=self.roland_predict)

        grass_pred_cmd = subparsers.add_parser("grass-pred")
        grass_pred_cmd.set_defaults(subcommand=self.stutt_herto_predict)

        grass_wta_pred_cmd = subparsers.add_parser("grass-pred-wta")
        grass_wta_pred_cmd.set_defaults(subcommand=self.stutt_herto_wta_predict)

        roland_pred_history_cmd = subparsers.add_parser("roland-pred-history")
        roland_pred_history_cmd.set_defaults(subcommand=self.roland_predict_history)

        roland_pred_wta_cmd = subparsers.add_parser("roland-pred-wta")
        roland_pred_wta_cmd.set_defaults(subcommand=self.roland_predict_wta)

        roland_pred_wta_history_cmd = subparsers.add_parser("roland-pred-wta-history")
        roland_pred_wta_history_cmd.set_defaults(subcommand=self.roland_predict_wta_history)

        print_feature_importance_cmd = subparsers.add_parser("features")
        print_feature_importance_cmd.set_defaults(
            subcommand=self.print_feature_importance
        )

    def handle(self, *args, **options):
        options["subcommand"](options)

    def roland(self, options):
        tennis_prediction()

    def wimbledon_atp(self, options):
        wimbledon()

    def wimbledon_wta_model(self, options):
        wimbledon_wta()

    def wimbledon_predict(self, options):
        wimbledon_pred()

    def wimbledon_predict_wta(self, options):
        wimbledon_pred_wta()

    def stutt_herto(self, options):
        grass_prediction()

    def stutt_herto_wta(self, options):
        wta_grass_prediction()

    def roland_wta(self, options):
        tennis_prediction_wta()

    def roland_predict(self, options):
        predict_matches()

    def stutt_herto_predict(self, options):
        predict_stutt_herto_matches()

    def stutt_herto_wta_predict(self, options):
        predict_stutt_herto_wta_matches()

    def roland_predict_history(self, options):
        predict_matches_history()

    def roland_predict_wta(self, options):
        predict_matches_wta()

    def roland_predict_wta_history(self, options):
        predict_matches_wta_history()

    def print_feature_importance(self, options):
        feature_importance()
