import pandas as pd
import requests
import json
from vakio.task.sport_wager import create_multiscore_wager
from ast import literal_eval
from vakio.models import MonivetoOdds
import os
import time
from datetime import datetime
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import concurrent
from django.db.utils import IntegrityError
from vakio.task.moniveto import moniveto

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)
moniveto_id = moniveto.moniveto_id
list_index = moniveto.list_index
bonus = 0
scores = [
        "0,1,2,3,4,5,6,7-0,1,2,3",
        "0,1,2,3,4-0,1,2,3,4",
        "0,1,2,3,4-0,1,2,3,4",
        #"0,1,2,3,4,5,6-0,1,2,3",
        #"0,1,2,3,4-0,1,2,3,4",
    ]


def get_sport_winshare(draw_id, matches, scores):
    host = "https://www.veikkaus.fi"
    r = requests.post(
        host + f"/api/sport-odds/v1/games/MULTISCORE/draws/{draw_id}/odds",
        verify=True,
        data=matches,
        headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-ESA-API-Key': 'ROBOT'
            })

    data = r.text
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        logging.error(e)
        logging.error(data)

    odds_list = []
    for row in data['odds']:
        #logging.info(row)
        #exit(1)
        selections = row['selections']
        id = ''
        matches = []
        for selection in selections:
            home = selection['homeScores'][0]
            away = selection['awayScores'][0]
            id += f"{home}-{away},"
            matches.append(f"{home}-{away}")
        id = id[:-1]
        value = row['value']
        if value == -200:
            try:
                value = (data['exchange'] + bonus) / 2
            except TypeError:
                logging.error(data)
                exit(1)

        if len(matches) == 4:
            monivetoodds = MonivetoOdds(
                combination=id,
                list_index=list_index,
                moniveto_id=moniveto_id,
                value=value,
                match1= '0-' + matches[0],
                match2= '1-' + matches[1],
                match3= '2-' + matches[2],
                match4= '3-' + matches[3],
            )
            odds_list.append(monivetoodds)
        elif len(matches) == 2:
            monivetoodds = MonivetoOdds(
                combination=id,
                list_index=list_index,
                moniveto_id=moniveto_id,
                value=value,
                match1= '0-' + matches[0],
                match2= '1-' + matches[1],
            )
            odds_list.append(monivetoodds)
        else:
            monivetoodds = MonivetoOdds(
                combination=id,
                list_index=list_index,
                moniveto_id=moniveto_id,
                value=value,
                match1='0-' + matches[0],
                match2='1-' + matches[1],
                match3='2-' + matches[2],
            )
            odds_list.append(monivetoodds)
    return odds_list


def get_odds(data, page):
    data['page'] = page
    data['selections'] = data["boards"][0]["selections"]
    matches = json.dumps(data)
    try:
        odds = get_sport_winshare(moniveto_id, matches, scores)
    except requests.exceptions.SSLError as e:
        logging.error(e)
        time.sleep(5)
        try:
            odds = get_sport_winshare(moniveto_id, matches, scores)
        except requests.exceptions.SSLError as e:
            logging.error(e)
            time.sleep(5)
            odds = get_sport_winshare(moniveto_id, matches, scores)
    return odds


def moniveto_winshares():
    start = datetime.now()
    count = 1
    for score in scores:
        home, away = score.split('-')
        count = count * len(home.split(',')) * len(away.split(','))
    logging.info(f"Total combinations: {count}")

    data = create_multiscore_wager(moniveto_id, 0, scores)

    MonivetoOdds.objects.filter(moniveto_id=moniveto_id, list_index=list_index).delete()

    total_pages = int(count / 100) + 1
    logging.info(f"Total pages: {total_pages}")
    page = 0
    batch = 100
    while page < total_pages:
        print(f"Page: {page} / {page + batch}")
        objects = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(get_odds, data, i) for i in range(page, page + batch)]
            for future in concurrent.futures.as_completed(futures):
                odds_data = future.result()
                objects += odds_data

        # bulk_create will make only one query to the database.
        try:
            MonivetoOdds.objects.bulk_create(objects)
            #MonivetoOdds.objects.bulk_update(objects, ['value'])
        except IntegrityError as e:
            logging.error(e)
            for item in objects:
                try:
                    item.save()
                except Exception as e:
                    logging.error(e)
                    pass

        page += batch

    # Getting current time and log when the script ends
    end = datetime.now()
    logging.info('Script ended')

    logging.info('Time elapsed: {}'.format(end - start))
