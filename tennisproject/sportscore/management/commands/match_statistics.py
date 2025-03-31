import concurrent.futures
import json
import logging
import time
from typing import Any, Dict, List

import requests
from django.db.models import Q
from sportscore.models import Stats
from tennisapi.models import AtpMatches, WtaMatches
from tqdm import tqdm


class MatchStatisticsFetcher:
    def __init__(self, sport_score_key: str):
        self.sport_score_key = sport_score_key
        self.headers = {
            "X-RapidAPI-Key": sport_score_key,
            "X-RapidAPI-Host": "sportscore1.p.rapidapi.com",
        }

    def get_match_ids(self) -> List[int]:
        """Fetch ATP and WTA match IDs."""
        atp_ids = list(
            AtpMatches.objects.filter(Q(date__gt="2025-2-15")).values_list(
                "event_id", flat=True
            )
        )

        wta_ids = list(
            WtaMatches.objects.filter(Q(date__gt="2025-2-15")).values_list(
                "event_id", flat=True
            )
        )

        return atp_ids + wta_ids

    def fetch_statistics(self, match_id: int) -> Dict[str, Any]:
        """Fetch statistics for a single match with retry logic."""
        url = f"https://sportscore1.p.rapidapi.com/events/{match_id}/statistics"
        max_retries = 4
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data
            except requests.exceptions.RequestException as e:
                if "Too Many Requests for url" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                logging.error(f"Error fetching data for match {match_id}: {str(e)}")
                return None
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON for match {match_id}: {str(e)}")
                return None

    def process_match(self, match_id: int) -> None:
        """Process a single match and save its statistics."""
        data = self.fetch_statistics(match_id)
        if data:
            try:
                # Update or create the match statistics
                Stats.objects.update_or_create(id=match_id, defaults={"data": data})
                #Stats.objects.create(id=match_id, data=data)
            except Exception as e:
                logging.error(f"Error saving stats for match {match_id}: {str(e)}")

    def match_statistics(self, options: Dict[str, Any]) -> None:
        """Fetch and save statistics for all matches in parallel."""
        match_ids = self.get_match_ids()
        logging.info(f"Total ids to fetch: {len(match_ids)}")

        # Configure the thread pool size based on your needs
        max_workers = min(
            10, len(match_ids)
        )  # Adjust the maximum number of workers as needed

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a list of future objects
            futures = [
                executor.submit(self.process_match, match_id) for match_id in match_ids
            ]

            # Monitor progress with tqdm
            for _ in tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Fetching match statistics",
            ):
                pass


def main():
    fetcher = MatchStatisticsFetcher(settings.SPORT_SCORE_KEY)
    fetcher.match_statistics({})
