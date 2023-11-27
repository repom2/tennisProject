import pandas as pd
import requests
import json
from vakio.task.sport_wager import create_multiscore_wager
from ast import literal_eval
from vakio.models import WinShare
import os


def get_sport_winshare(draw_id, matches):
    host = "https://www.veikkaus.fi"
    r = requests.post(
        host + f"/api/sport-odds/v1/games/MULTISCORE/draws/{draw_id}/odds",
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
        """WinShare.objects.update_or_create(
            id="".join(board),
            defaults={
                "value": winshare["value"],
                "bets": winshare["numberOfBets"],
            }
        )"""
    return j['hasNext']


def moniveto_winshares():
    scores = ["0-0,1", "2-3,4", "4-2,5"]
    moniveto = "63088"
    data = create_multiscore_wager(moniveto, 0, scores)

    print(data)

    page = 1
    has_next = True
    while has_next:
        data['page'] = page
        matches = json.dumps(data)
        has_next = get_sport_winshare(moniveto, matches)
        page += 1
        print(page)




