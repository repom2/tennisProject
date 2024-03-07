from vakio.models import WinShare, Combination
import pandas as pd
from vakio.task.sport_wager import create_sport_wager
import requests
import json
import time
import datetime
import logging
from vakio.task import probs

list_index = probs.list_index
vakio_id = probs.vakio_id
max_bet_eur = 15
line_cost = 0.1
stake = line_cost * 100

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

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
    "listIndex": list_index,
    "id": vakio_id,
    "miniVakio": False,
    "input": "",
    "stake": 0
}


def get_sport_winshare(draw, matches):
    host = "https://www.veikkaus.fi"
    r = requests.post(
        host + "/api/sport-winshare/v1/games/SPORT/draws/" + str(draw) + "/winshare",
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

        # print("value=%d,numberOfBets=%d,board=%s" % (
        # winshare["value"], winshare["numberOfBets"], "".join(board)))

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
        return True
    else:
        print("Request failed:\n" + r.text)
        return False


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
    query = f"""
    select id, bets, prob, win, yield, combination, value, share from 
        (select a.id, b.bets, prob, bet, a.combination,
            b.value / 100 as win, 
            round((prob*(b.value*0.01/({line_cost})))::numeric, 4) as yield,
            ((b.value * 0.01) * (prob) - 1) / (b.value * 0.01) * 10000 as share,
            b.value as value
    from vakio_combination a 
    inner join vakio_winshare b on b.combination=a.combination and 
        b.vakio_id = a.vakio_id and b.list_index = a.list_index
    where bet = False and b.vakio_id = {params["id"]} and b.list_index = {params["listIndex"]}
    ) s  order by yield desc
    """
    data = WinShare.objects.raw(query)
    logging.info("Number of lines: %d", len(data))
    logging.info(params)
    df = pd.DataFrame([item.__dict__ for item in data])
    columns = ['combination', 'bets', 'prob', 'win', 'yield', 'value', 'share']
    #df = df[df['yield'] >= 1]
    #df = df[df['share'] >= 0]
    #df = df[df['bets'] == 1]
    print("Profitable lines:", len(df))
    df = df[columns]

    max_bet = int(max_bet_eur / line_cost)
    df = df.head(max_bet)
    print("Max Bet length:", len(df), "lines to bet", max_bet)
    print(df)

    matches = []
    for index, row in df.iterrows():
        line = list(row['combination'])
        if matches == []:
            for i in line:
                if i == '1':
                    matches.append([1, 0, 0])
                elif i == 'X':
                    matches.append([0, 1, 0])
                else:
                    matches.append([0, 0, 1])
        else:
            for i in range(len(matches)):
                if line[i] == '1':
                    matches[i][0] += 1
                elif line[i] == 'X':
                    matches[i][1] += 1
                else:
                    matches[i][2] += 1
    for i in range(len(matches)):
        matches[i] = [round(x / len(df), 2) for x in matches[i]]
        logging.info(matches[i])
    exit()
    session = login(params["username"], params["password"])
    for index, row in df.iterrows():
        print(row['combination'])
        line = list(row['combination'])

        # Data for wager
        data = create_sport_wager(params["listIndex"], stake, line, False)
        # Data for winshare
        win_data = create_sport_wager(params["id"], 0, line, False)
        matches = json.dumps(win_data)
        winshare = get_sport_winshare(params["id"], matches)
        bet_limit = row["prob"]*(winshare/stake)
        if bet_limit < 1.0:
            print("BET LIMIT EXCEEDED, bet limit:", bet_limit)
            continue
        print("BET:", "winshare:", winshare, "bet limit:", bet_limit)
        is_bet_placed = place_wagers(data, session)

        balance = get_balance(session)
        print("\n\taccount balance: %.2f\n" % (balance / 100.0))
        if is_bet_placed:
            Combination.objects.update_or_create(
                combination=row["combination"],
                vakio_id=params["id"],
                list_index=params["listIndex"],
                defaults={
                    "bet": True,
                    "value": winshare,
                }
        )
