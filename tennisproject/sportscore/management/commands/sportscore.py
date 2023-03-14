import requests
import os


class Command(BaseCommand):
    """Sportscore Data"""

    def add_arguments(self, parser):
        list_sports_cmd = subparsers.add_parser("list-custom-fields")
        list_sports_cmd.set_defaults(subcommand=self.list_sports)

    def list_sports(self):
        url = "https://sportscore1.p.rapidapi.com/sports"
        sport_score_key = os.getenv('SPORT_SCORE_KEY')
        headers = {
            "X-RapidAPI-Key": sport_score_key,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)

        print(response.text)