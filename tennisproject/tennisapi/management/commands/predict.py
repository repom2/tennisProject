from django.core.management.base import BaseCommand
from tennisapi.ml.ml_model import train_model
from tennisapi.ml.predict import predict
from tennisapi.ml.insert_data_to_match import insert_data_to_match
from tennisapi.ml.model_interact import feature_importance
from tennisapi.ml.train_model import train_ml_model


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        train_ml_model_cmd = subparsers.add_parser("oldtrain")
        train_ml_model_cmd.set_defaults(subcommand=self.train_ml_model)

        train_model_cmd = subparsers.add_parser("train-model")
        train_model_cmd.set_defaults(subcommand=self.train_model)

        predict_matches_cmd = subparsers.add_parser("pred")
        predict_matches_cmd.set_defaults(subcommand=self.predict_matches)
        predict_matches_cmd.add_argument("pred", type=str, default='atp')
        predict_matches_cmd.add_argument("tour", type=str, default='zhu')

        train_cmd = subparsers.add_parser("insert-match")
        train_cmd.set_defaults(subcommand=self.insert_data_to_matches)
        train_cmd.add_argument("train", type=str, default='atp')
        train_cmd.add_argument("tour", type=str, default='zhu')

        print_feature_importance_cmd = subparsers.add_parser("features")
        print_feature_importance_cmd.set_defaults(
            subcommand=self.print_feature_importance
        )

    def handle(self, *args, **options):
        options["subcommand"](options)

    def predict_matches(self, options):
        level = options["pred"]
        tour = options["tour"]
        predict(level, tour)

    def insert_data_to_matches(self, options):
        level = options["train"]
        tour = options["tour"]
        insert_data_to_match(level, tour)

    def print_feature_importance(self, options):
        feature_importance()

    def train_ml_model(self, options):
        train_model()

    def train_model(self, options):
        train_ml_model()
