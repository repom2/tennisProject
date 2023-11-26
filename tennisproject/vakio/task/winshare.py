import pandas as pd
import requests
import json
from vakio.task.sport_wager import create_sport_wager
from ast import literal_eval
from vakio.models import WinShare
import os


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
    matches = ["1X2", "1X2", "1X2", "1X2", "1X2", "1X2", "1X2", "1X2", "1X2", "1X2", "1X2", "1X2"]
    data = create_sport_wager("", 0, matches, False)

    page = 1
    has_next = True
    while has_next:
        data['page'] = page
        print(data)
        matches = json.dumps(data)
        has_next = get_sport_winshare("55446", matches)
        print(has_next)
        page += 1