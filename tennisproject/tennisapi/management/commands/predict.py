from django.core.management.base import BaseCommand
from tennisapi.ml.atlanta import atlanta
from tennisapi.ml.ml_model import train_model
from tennisapi.ml.predict import predict
from tennisapi.ml.warsaw_wta import warsaw_wta
from tennisapi.ml.warsaw_wta_pred import warsaw_pred_wta
from tennisapi.ml.atlanta_pred import atlanta_pred
from tennisapi.ml.model_interact import feature_importance


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        atlanta_cmd = subparsers.add_parser("atlanta")
        atlanta_cmd.set_defaults(subcommand=self.atlanta_atp)

        atlanta_pred_cmd = subparsers.add_parser("atlanta-pred")
        atlanta_pred_cmd.set_defaults(subcommand=self.atlanta_pred)

        warsaw_wta_cmd = subparsers.add_parser("warsaw-wta")
        warsaw_wta_cmd.set_defaults(subcommand=self.warsaw_wta)

        warsaw_pred_cmd = subparsers.add_parser("warsaw-pred")
        warsaw_pred_cmd.set_defaults(subcommand=self.warsaw_predict)

        train_ml_model_cmd = subparsers.add_parser("train")
        train_ml_model_cmd.set_defaults(subcommand=self.train_ml_model)

        predict_matches_cmd = subparsers.add_parser("pred")
        predict_matches_cmd.set_defaults(subcommand=self.predict_matches)
        predict_matches_cmd.add_argument("pred", type=str, default='atp')
        predict_matches_cmd.add_argument("tour", type=str, default='zhu')

        print_feature_importance_cmd = subparsers.add_parser("features")
        print_feature_importance_cmd.set_defaults(
            subcommand=self.print_feature_importance
        )

    def handle(self, *args, **options):
        options["subcommand"](options)

    def atlanta_atp(self, options):
        atlanta()

    def atlanta_pred(self, options):
        atlanta_pred()

    def warsaw_predict(self, options):
        warsaw_pred_wta()

    def warsaw_wta(self, options):
        warsaw_wta()

    def predict_matches(self, options):
        level = options["pred"]
        tour = options["tour"]
        predict(level, tour)

    def print_feature_importance(self, options):
        feature_importance()

    def train_ml_model(self, options):
        train_model()
