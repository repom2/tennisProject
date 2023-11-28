import pandas as pd
import requests
import json
from vakio.task.sport_wager import create_sport_wager
from ast import literal_eval
from vakio.models import WinShare
import os
import logging
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)


def get_sport_winshare(draw, matches):
    host = "https://www.veikkaus.fi"
    r = requests.post(
        host + "/api/sport-winshare/v1/games/SPORT/draws/" + draw + "/winshare",
        verify=True, data=matches, headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-ESA-API-Key': 'ROBOT'
            })
    j = r.json()
    print(j)
    for winshare in j["winShares"]:
        # each winshare has only one selection that contains the board (outcomes)

        board = []
        for selection in winshare["selections"]:
            for outcome in selection["outcomes"]:
                board.append(outcome)

        print("value=%d,numberOfBets=%d,board=%s" % (
        winshare["value"], winshare["numberOfBets"], "".join(board)))

        # save to db
        WinShare.objects.update_or_create(
            id="".join(board),
            defaults={
                "value": winshare["value"],
                "bets": winshare["numberOfBets"],
            }
        )
    return j['hasNext']


def get_win_share():
    start = datetime.now()
    matches = ["1X2"] * 12
    vakio_id = "55449"
    data = create_sport_wager("", 0, matches, False)

    page = 1
    has_next = True
    while has_next:
        data['page'] = page
        matches = json.dumps(data)
        has_next = get_sport_winshare(vakio_id, matches)
        page += 1

    # Getting current time and log when the script ends
    end = datetime.now()
    logging.info('Script ended')

    logging.info('Time elapsed: {}'.format(end - start))
