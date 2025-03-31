import concurrent.futures
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

import requests
from django.db.utils import IntegrityError
from vakio.models import Moniveto, MonivetoOdds
from vakio.task.sport_wager import create_multiscore_wager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

VEIKKAUS_API_HOST = "https://www.veikkaus.fi"
BONUS = 0
BATCH_SIZE = 100
MAX_WORKERS = 20
MAX_RETRIES = 5
RETRY_DELAY = 5

SCORES_DEFAULT = [
    "0,1,2,3,4,5,6,7-0,1,2,3",
    "0,1,2,3,4-0,1,2,3,4,5",
    "0,1,2,3,4,5-0,1,2,3,4",
]


class MonivetoDataFetcher:
    def __init__(self, moniveto_id: int, list_index: int):
        self.moniveto_id = moniveto_id
        self.list_index = list_index
        self.scores = self._get_scores()
        self.exchange = 0

    def _get_scores(self) -> List[str]:
        saved_scores = (
            Moniveto.objects.filter(
                moniveto_id=self.moniveto_id, list_index=self.list_index
            )
            .values_list("scores", flat=True)
            .first()
        )
        #saved_scores = None
        if saved_scores is None:
            logger.warning("No scores found, using default scores")
            return SCORES_DEFAULT
        return saved_scores

    @staticmethod
    def fetch_odds_data(draw_id: int, matches: str) -> Dict[str, Any]:
        for _ in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"{VEIKKAUS_API_HOST}/api/sport-odds/v1/games/MULTISCORE/draws/{draw_id}/odds",
                    verify=True,
                    data=matches,
                    headers={
                        "Content-type": "application/json",
                        "Accept": "application/json",
                        "X-ESA-API-Key": "ROBOT",
                    },
                )
                return response.json()  # Return the complete response data
            except (requests.exceptions.SSLError, json.JSONDecodeError) as e:
                logger.error(f"Error fetching odds data: {e}")
                time.sleep(RETRY_DELAY)
        raise Exception("Failed to fetch odds data after maximum retries")

    def _create_moniveto_odds(self, row: Dict[str, Any], exchange: float) -> MonivetoOdds:
        selections = row["selections"]
        matches = []
        id_parts = []

        for selection in selections:
            home = selection["homeScores"][0]
            away = selection["awayScores"][0]
            id_parts.append(f"{home}-{away}")
            matches.append(f"{home}-{away}")

        combination_id = ",".join(id_parts)
        value = row["value"]

        if value == -200:
            value = (exchange + BONUS) / 2

        odds_data = {
            "combination": combination_id,
            "list_index": self.list_index,
            "moniveto_id": self.moniveto_id,
            "value": value,
        }

        for i, match in enumerate(matches, 1):
            odds_data[f"match{i}"] = f"{i-1}-{match}"

        return MonivetoOdds(**odds_data)

    def process_page(self, page: int, data: Dict[str, Any]) -> List[MonivetoOdds]:
        data["page"] = page
        data["selections"] = data["boards"][0]["selections"]
        matches = json.dumps(data)

        response_data = self.fetch_odds_data(self.moniveto_id, matches)
        exchange = response_data.get("exchange", 0)
        try:
            return [self._create_moniveto_odds(row, exchange) for row in response_data["odds"]]
        except KeyError as e:
            logger.error(f"response_data: {response_data}")
            raise

    def calculate_total_combinations(self) -> int:
        total = 1
        for score in self.scores:
            home, away = score.split("-")
            total *= len(home.split(",")) * len(away.split(","))
        return total

    def fetch_all_odds(self):
        start_time = datetime.now()
        logger.info(
            f"Starting odds fetching for moniveto_id: {self.moniveto_id}, list_index: {self.list_index}"  # noqa E501
        )

        # Update scores in database
        Moniveto.objects.filter(
            moniveto_id=self.moniveto_id, list_index=self.list_index
        ).update(scores=self.scores)

        total_combinations = self.calculate_total_combinations()
        total_pages = (total_combinations + BATCH_SIZE - 1) // BATCH_SIZE

        logger.info(
            f"Total combinations: {total_combinations}, Total pages: {total_pages}"
        )

        # Clear existing odds
        MonivetoOdds.objects.filter(
            moniveto_id=self.moniveto_id, list_index=self.list_index
        ).delete()

        base_data = create_multiscore_wager(self.moniveto_id, 0, self.scores)

        for batch_start in range(0, total_pages, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, total_pages)

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=MAX_WORKERS
            ) as executor:
                futures = [
                    executor.submit(self.process_page, page, base_data.copy())
                    for page in range(batch_start, batch_end)
                ]

                odds_objects = []
                for future in concurrent.futures.as_completed(futures):
                    odds_objects.extend(future.result())

            self._save_odds_batch(odds_objects)

        duration = datetime.now() - start_time
        logger.info(f"Completed in {duration}")

    def _save_odds_batch(self, odds_objects: List[MonivetoOdds]):
        try:
            MonivetoOdds.objects.bulk_create(odds_objects)
        except IntegrityError as e:
            logger.error(f"Bulk create failed: {e}")
            for obj in odds_objects:
                try:
                    obj.save()
                except Exception as e:
                    logger.error(f"Failed to save individual object: {e}")


def moniveto_winshares(list_index: int, moniveto_id: int):
    if moniveto_id is None:
        raise ValueError("No moniveto_id found")

    fetcher = MonivetoDataFetcher(moniveto_id, list_index)
    fetcher.fetch_all_odds()
