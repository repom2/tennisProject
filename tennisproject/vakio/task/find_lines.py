from vakio.models import WinShare, Combination
import pandas as pd
from vakio.task.sport_wager import create_sport_wager
import requests
import json
import time
import datetime

# the veikkaus site address
host = "https://www.veikkaus.fi"

headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'X-ESA-API-Key': 'ROBOT'
}

params = {
    "username": "repom",
    "password": "_W14350300n1",
    "game": "SPORT",
    "draw": "",
    "listIndex": "6",
    "id": "55450",
    "miniVakio": False,
    "input": "",
    "stake": 0
}


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

        #print("value=%d,numberOfBets=%d,board=%s" % (
        #winshare["value"], winshare["numberOfBets"], "".join(board)))

    return winshare["value"]


def login(username, password):
    s = requests.Session()
    login_req = {
        "type": "STANDARD_LOGIN",
        "login": username,
        "password": password
    }
    r = s.post(
        "https://www.veikkaus.fi/api/bff/v1/sessions",
        data=json.dumps(login_req),
        headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'X-ESA-API-Key': 'ROBOT'
        }
    )
    if r.status_code == 200:
        return s
    else:
        raise Exception("Authentication failed", r.status_code)


# Place wagers on the system.
# Prints out the serial numbers of all accepted wagers
# and error codes for rejected wagers.

def place_wagers(wager_req, session):
    rt = time.time()
    r = session.post(
        host + "/api/sport-interactive-wager/v1/tickets",
        verify=True,
        data=json.dumps(wager_req),
        headers=headers
    )
    rt = time.time() - rt;

    if r.status_code == 200:
        j = r.json()
        print("%s - placed wager in %.3f seconds, serial %s\n" % (datetime.datetime.now(), rt, j["serialNumber"][:17]))
    else:
        print("Request failed:\n" + r.text)


def get_balance(session):
    r = session.get(
        host + "/api/v1/players/self/account",
        verify=True,
        headers=headers
    )
    j = r.json()
    return j["balances"]["CASH"]["usableBalance"]


# https://github.com/VeikkausOy/sport-games-robot/blob/master/Python/robot.py
def find_lines():
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
    where yield > 0.3 and bet = False order by yield desc
    """
    data = WinShare.objects.raw(query)

    df = pd.DataFrame([item.__dict__ for item in data])
    columns = ['id', 'bets', 'value', 'prob', 'win', 'yield']
    #df = df[df['yield'] > 0.1]
    df = df[columns]

    max_bet = int(max_bet_eur / line_cost)
    #df = df.head(max_bet)
    print("length:", len(df), max_bet)
    print(df)

    session = login(params["username"], params["password"])
    for index, row in df.iterrows():
        print(row['id'])
        line = list(row['id'])

        # Data for wager
        data = create_sport_wager(params["listIndex"], stake, line, False)
        # Data for winshare
        win_data = create_sport_wager(params["id"], 0, line, False)
        matches = json.dumps(win_data)
        winshare = get_sport_winshare(params["id"], matches)
        bet_limit = row["prob"]*(winshare/(stake+1))
        if bet_limit < 1.0:
            print("bet limit:", bet_limit)
            continue
        place_wagers(data, session)

        balance = get_balance(session)
        #print("\n\taccount balance: %.2f\n" % (balance / 100.0))
        Combination.objects.update_or_create(
            id=row["id"],
            defaults={
                "bet": True,
            }
        )
