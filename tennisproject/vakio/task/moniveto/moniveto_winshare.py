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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)


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

    for row in data['odds']:
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
            value = data['exchange'] / 2
        # save to db""
        if len(matches) == 4:
            MonivetoOdds.objects.update_or_create(
                id=id,
                defaults={
                    "value": value,
                    "match1": '0-' + matches[0],
                    "match2": '1-' + matches[1],
                    "match3": '2-' + matches[2],
                    "match4": '3-' + matches[3],
                }
            )
        else:
            MonivetoOdds.objects.update_or_create(
                id=id,
                defaults={
                    "value": value,
                    "match1": '0-' + matches[0],
                    "match2": '1-' + matches[1],
                    "match3": '2-' + matches[2],
                }
            )
    return data['hasNext']


def moniveto_winshares():
    start = datetime.now()
    scores = [
        "0,1,2,3,4,5-0,1,2,3,4,5",
        "0,1,2,3,4,5-0,1,2,3,4,5",
        "0,1,2,3,4,5-0,1,2,3,4,5",
    ]

    count = 0
    for score in scores:
        home, away = score.split('-')
        count += len(home.split(',')) * len(away.split(','))

    moniveto = "63135"
    data = create_multiscore_wager(moniveto, 0, scores)
    MonivetoOdds.objects.all().delete()
    page = 1
    has_next = True

    with tqdm(total=count) as pbar:
        while has_next:
            data['page'] = page
            data['selections'] = data["boards"][0]["selections"]
            matches = json.dumps(data)
            has_next = get_sport_winshare(moniveto, matches, scores)
            page += 1
            pbar.update(100)

    # Getting current time and log when the script ends
    end = datetime.now()
    logging.info('Script ended')

    logging.info('Time elapsed: {}'.format(end - start))
