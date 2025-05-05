from django.core.management.base import BaseCommand
from tennisapi.ml.ml_model import train_model
from tennisapi.ml.predict import predict
from tennisapi.ml.predict_ta import predict_ta
from tennisapi.ml.insert_data_to_match import insert_data_to_match
from tennisapi.ml.model_interact import feature_importance
from tennisapi.ml.train_model import train_ml_model
from tennisapi.ml.bet_results import bet_results
from tennisapi.history.history_bet import history_bet
from tennisapi.history.bet_bet import bet_bet


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

        pred_matches_cmd = subparsers.add_parser("predict")
        pred_matches_cmd.set_defaults(subcommand=self.pred_matches)
        pred_matches_cmd.add_argument("pred", type=str, default='atp')
        pred_matches_cmd.add_argument("tour", type=str, default='zhu')

        train_cmd = subparsers.add_parser("insert-match")
        train_cmd.set_defaults(subcommand=self.insert_data_to_matches)
        train_cmd.add_argument("train", type=str, default='atp')
        train_cmd.add_argument("tour", type=str, default='zhu')

        print_feature_importance_cmd = subparsers.add_parser("features")
        print_feature_importance_cmd.set_defaults(
            subcommand=self.print_feature_importance
        )

        results_cmd = subparsers.add_parser("results")
        results_cmd.set_defaults(subcommand=self.results)

        history_cmd = subparsers.add_parser("history-bet")
        history_cmd.set_defaults(subcommand=self.history_bet)

        history_cmd = subparsers.add_parser("bet-bet")
        history_cmd.set_defaults(subcommand=self.bet_bet)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def results(self, options):
        bet_results()

    def history_bet(self, options):
        history_bet()

    def bet_bet(self, options):
        bet_bet()

    def predict_matches(self, options):
        level = options["pred"]
        tour = options["tour"]
        predict(level, tour)

    def pred_matches(self, options):
        level = options["pred"]
        tour = options["tour"]
        predict_ta(level, tour)

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
