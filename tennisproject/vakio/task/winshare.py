import pandas as pd
import requests
import json
from vakio.task.sport_wager import create_sport_wager
from ast import literal_eval
from vakio.models import WinShare, Combination
import os
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import concurrent
import math
from django.db.utils import IntegrityError
from vakio.task import probs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

#list_index = probs.list_index
#vakio_id = probs.vakio_id
#number_of_matches = probs.number_of_matches


def get_sport_winshare(draw, matches, list_index):
    host = "https://www.veikkaus.fi"
    r = requests.post(
        host + "/api/sport-winshare/v1/games/SPORT/draws/" + str(draw) + "/winshare",
        verify=True, data=matches, headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-ESA-API-Key': 'ROBOT'
            })
    j = r.json()
    odds_list = []
    #logging.info(j)
    try:
        j["winShares"]
    except KeyError as e:
        logging.info(f"KeyError: {e}")
        logging.info(j)
        exit(1)
    for winshare in j["winShares"]:
        # each winshare has only one selection that contains the board (outcomes)
        board = []
        for selection in winshare["selections"]:
            for outcome in selection["outcomes"]:
                board.append(outcome)

        # logging.info("value=%d,numberOfBets=%d,board=%s" % (
        # winshare["value"], winshare["numberOfBets"], "".join(board)))

        vakio_odds = WinShare(
            vakio_id=str(draw),
            list_index=str(list_index),
            combination="".join(board),
            value=winshare["value"],
            bets=winshare["numberOfBets"],
        )
        odds_list.append(vakio_odds)

    return odds_list


def combine_strings(str1, str2):
    combined = []
    # zip stops generating tuples when shorter string exhausts
    for ch1, ch2 in zip(str1, str2):
        if ch1 == ch2:
            combined.append(ch1)
        else:
            combined.append(ch1 + ch2)
    return combined


def get_values(data, page, vakio_id, list_index):
    data['page'] = page
    matches = json.dumps(data)
    time.sleep(1)
    try:
        values = get_sport_winshare(vakio_id, matches, list_index)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.JSONDecodeError,
            requests.exceptions.SSLError) as e:
        logging.info('ConnectionError, waiting 5 seconds')
        time.sleep(5)
        try:
            values = get_sport_winshare(vakio_id, matches, list_index)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.JSONDecodeError,
                requests.exceptions.SSLError) as e:
            logging.info('ConnectionError, waiting 5 seconds, 2')
            time.sleep(5)
            values = get_sport_winshare(vakio_id, matches, list_index)
    return values


def get_win_share(list_index, vakio_id):
    number_of_matches = Combination.objects.filter(vakio_id=vakio_id, list_index=list_index).values('combination').first()
    number_of_matches = len(number_of_matches['combination'])
    start = datetime.now()
    matches = [["1", "X", "2"]] * number_of_matches
    if vakio_id == 55570:
        print("Removed", matches[2])
        matches[0] = ["1", "X"]
        matches[6] = ["1", "X"]


    logging.info(f"List index: {list_index} - Vakio id: {vakio_id} - Number of matches: {number_of_matches}")

    nro_of_combinations = 1
    for row in matches:
        nro_of_combinations = nro_of_combinations * len(row)
    #number_of_matches = 12
    logging.info(f"Matches: {matches}")
    #nro_of_combinations = pow(3, 12)
    logging.info(f"Total combinations: {nro_of_combinations}")

    data = create_sport_wager("", 0, matches, False)
    WinShare.objects.filter(vakio_id=vakio_id, list_index=list_index).delete()

    total_pages = math.ceil(nro_of_combinations / 100) + 1
    logging.info(f"Total pages: {total_pages}")
    page = 0
    batch = 100

    while page < total_pages:
        print(f"Page: {page} / {page + batch}")
        objects = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(get_values, data, i, vakio_id, list_index) for i in range(page, page + batch)]
            for future in concurrent.futures.as_completed(futures):
                odds_data = future.result()
                objects += odds_data
        # bulk_create will make only one query to the database.
        try:
            WinShare.objects.bulk_create(objects)
        except IntegrityError as e:
            logging.error(e)
            for item in objects:
                try:
                    item.save()
                except Exception as e:
                    logging.error(e)
                    pass

        page += batch

    end = datetime.now()
    logging.info('Script ended')

    logging.info('Time elapsed: {}'.format(end - start))
