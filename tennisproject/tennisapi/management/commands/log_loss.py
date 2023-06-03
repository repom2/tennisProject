from django.core.management.base import BaseCommand
from tennisapi.ml.log_loss_wta import log_loss_wta
from tennisapi.ml.log_loss_pred import log_loss_pred


class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="subcommands", dest="subcommand", required=True
        )

        log_loss_wta_cmd = subparsers.add_parser("log-loss")
        log_loss_wta_cmd.set_defaults(
            subcommand=self.log_loss_wta_predict)

        log_loss_wta_pred_cmd = subparsers.add_parser("log-loss-pred")
        log_loss_wta_pred_cmd.set_defaults(
            subcommand=self.log_loss_wta_pred)

    def handle(self, *args, **options):
        options["subcommand"](options)

    def log_loss_wta_predict(self, options):
        log_loss_wta()

    def log_loss_wta_pred(self, options):
        log_loss_pred()
