from vakio.models import WinShare, Combination
import pandas as pd
from vakio.task.sport_wager import create_sport_wager
import requests
import json
import time
import datetime
from vakio.task.sport_wager import create_multiscore_wager

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
    "game": "MULTISCORE",
    "draw": "",
    "listIndex": "5",
    "id": "63088",
    "miniVakio": False,
    "input": "",
    "stake": 0
}


def get_sport_winshare(draw_id, matches):
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
    data = json.loads(data)
    print(data)
    for row in data['odds']:
        value = row['value'] / 2
        if value == -200:
            value = row['exchange'] / 2
    return value


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
def moniveto_bet():
    query = """
    select a.id, value * 0.1, (0.1 * value * b.prob * c.prob * d.prob * e.prob) as yield,
    (b.prob * c.prob * d.prob * e.prob) as prob 
    from vakio_monivetoodds a 
    inner join vakio_monivetoprob b on b.id=a.match1
    inner join vakio_monivetoprob c on c.id=a.match2
    inner join vakio_monivetoprob d on d.id=a.match3
    inner join vakio_monivetoprob e on e.id=a.match4
    order by yield desc
    """
    data = WinShare.objects.raw(query)

    df = pd.DataFrame([item.__dict__ for item in data])
    columns = ['id', 'prob',  'yield']
    df = df[df['yield'] > 1.0]
    df = df[columns]
    print(df.head(5))
    print("length:", len(df))

    max_bet_eur = 20
    line_cost = 0.05
    max_bet = int(max_bet_eur / line_cost)
    df = df.head(max_bet)
    print("length:", len(df))
    exit(0)
    session = login(params["username"], params["password"])
    for index, row in df.iterrows():
        print(row['id'])
        line = row['id'].split(',')
        print(line)
        # Data for wager
        data = create_multiscore_wager(params["listIndex"], 5, line)
        data['selections'] = data["boards"][0]["selections"]
        matches = json.dumps(data)
        winshare = get_sport_winshare(params["id"], matches)
        bet_limit = row["prob"]*winshare*0.1
        if bet_limit < 1.0:
            continue
        place_wagers(data, session)
        balance = get_balance(session)
        print("\n\taccount balance: %.2f\n" % (balance / 100.0))
        break
