from django.core.management.base import BaseCommand
from footballapi.ml.predict import predict
from footballapi.ml.bet_results import bet_results


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        predict_matches_cmd = subparsers.add_parser("pred")
        predict_matches_cmd.set_defaults(subcommand=self.predict_matches)
        predict_matches_cmd.add_argument("pred", type=str, default='premier')

        predict_all_cmd = subparsers.add_parser("all")
        predict_all_cmd.set_defaults(subcommand=self.predict_all_matches)

        results_cmd = subparsers.add_parser("results")
        results_cmd.set_defaults(subcommand=self.results)


    def handle(self, *args, **options):
        options["subcommand"](options)

    def predict_matches(self, options):
        level = options["pred"]
        predict(level)

    def results(self, options):
        bet_results()

    def predict_all_matches(self, options):
        predict('premier')
        predict('championship')
        predict('ligue1')
        predict('bundesliga')
        predict('seriea')
        predict('laliga')


