from django.core.management.base import BaseCommand
from tennis_api.ml.predict import predict
from tennis_api.ml.model_interact import feature_importance
from tennis_api.ml.bet_results import bet_results


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        predict_matches_cmd = subparsers.add_parser("pred")
        predict_matches_cmd.set_defaults(subcommand=self.predict_matches)
        predict_matches_cmd.add_argument("pred", type=str, default='atp')
        predict_matches_cmd.add_argument("tour", type=str, default='zhu')

        print_feature_importance_cmd = subparsers.add_parser("features")
        print_feature_importance_cmd.set_defaults(
            subcommand=self.print_feature_importance
        )

        results_cmd = subparsers.add_parser("results")
        results_cmd.set_defaults(subcommand=self.results)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def results(self, options):
        bet_results()

    def predict_matches(self, options):
        level = options["pred"]
        tour = options["tour"]
        predict(level, tour)

    def print_feature_importance(self, options):
        feature_importance()
