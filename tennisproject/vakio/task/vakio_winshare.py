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


def combine_strings(str1, str2):
    combined = []
    # zip stops generating tuples when shorter string exhausts
    for ch1, ch2 in zip(str1, str2):
        if ch1 == ch2:
            combined.append(ch1)
        else:
            combined.append(ch1 + ch2)
    return combined


def get_win_share_vakio():
    start = datetime.now()

    combinations = Combination.objects.all().values('id')
    df = pd.DataFrame(list(combinations))
    logging.info(df.tail(5))

    max_bet_eur = 2000
    line_cost = 0.1
    stake = 10
    query = f"""
        select id, bets, value, prob, win, yield from 
            (select a.id, b.bets, b.value, prob, bet,
                value / 100 as win, 
                round((prob*(value/({stake} + 1)))::numeric, 4) as yield
        from vakio_combination a 
        inner join vakio_winshare b on b.id=a.id) s 
        where yield > 1 and bet = False order by yield desc
        """
    data = WinShare.objects.raw(query)

    df = pd.DataFrame([item.__dict__ for item in data])
    columns = ['id', 'bets', 'value', 'prob', 'win', 'yield']
    # df = df[df['yield'] > 0.1]
    df = df[columns]
    logging.info(df.head(5))
    logging.info("Total combinations: {}".format(len(df)))

    matches = [
        ["1", "X", "2"],
        ["1", "X", "2"],
        ["1", "X", "2"],

        ["1", "2"],
        ["1", "2"],
        ["1", "X", "2"],

        ["1", "X", "2"],
        ["1", "2"],
        ["1", "X", "2"],

        ["1", "X", "2"],
        ["1", "2"],
        ["1", "2"],
        ["1", "2"],
    ]
    #matches = [["1", "X", "2"]] * 12
    vakio_id = "55456"
    data = create_sport_wager("", 0, matches, False)

    page = 1
    has_next = True
    while has_next:
        data['page'] = page
        matches = json.dumps(data)
        try:
            has_next = get_sport_winshare(vakio_id, matches)
        except requests.exceptions.ConnectionError:
            logging.info('ConnectionError, waiting 5 seconds')
            time.sleep(5)
            continue
        page += 1

    # Getting current time and log when the script ends
    end = datetime.now()
    logging.info('Script ended')

    logging.info('Time elapsed: {}'.format(end - start))
