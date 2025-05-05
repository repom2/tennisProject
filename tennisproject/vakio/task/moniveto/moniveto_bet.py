from vakio.models import MonivetoOdds, MonivetoBet, Moniveto
import pandas as pd
from vakio.task.sport_wager import create_sport_wager
import requests
import json
import time
from datetime import datetime
from vakio.task.sport_wager import create_multiscore_wager
import logging
from vakio.task.moniveto import moniveto
from tabulate import tabulate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

pd.set_option('display.max_rows', None)

# the veikkaus site address
host = "https://www.veikkaus.fi"

headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'X-ESA-API-Key': 'ROBOT'
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

    for row in data['odds']:
        value = row['value']
        if value == -200:
            value = data['exchange'] / 2
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
    rt = time.time() - rt

    if r.status_code == 200:
        j = r.json()
        # print("%s - placed wager in %.3f seconds, serial %s\n" % (datetime.now(), rt, j["serialNumber"][:17]))
        return True
    else:
        # print("Request failed:\n" + r.text)
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
def moniveto_bet(bet, max_bet_eur, list_index, moniveto_id):
    qs = Moniveto.objects.filter(moniveto_id=moniveto_id, list_index=list_index).first()
    start = datetime.now()
    logging.info(f"Moniveto bet started [{list_index}] [{moniveto_id}]")
    params = {
        "username": "repom",
        "password": "_W14350300n1",
        "game": "MULTISCORE",
        "draw": "",
        "listIndex": list_index,
        "id": moniveto_id,
        "miniVakio": False,
        "input": "",
        "stake": 0
    }
    stake = qs.stake
    line_cost = stake * 0.01
    if qs.home3 == '':
        m = 2
    elif qs.home4 == '' and qs.home3 is not None:
        m = 3
    else:
        m = 4
    logging.info(qs.home3)
    logging.info(qs.home4)
    logging.info(f"Matches in Moniveto: [{m}]")
    if m == 4:
        query = f"""
        select a.id, a.combination,
        (a.value * 0.01) * (b.prob * c.prob * d.prob * e.prob) as yield, bet.bet,
        (b.prob * c.prob * d.prob * e.prob) as prob, 
        a.value * 0.01 * {line_cost} as win,
        ((a.value * 0.01) * (b.prob * c.prob * d.prob * e.prob) - 1) / (a.value * 0.01) * 1000 as share
        from vakio_monivetoodds a 
        left join vakio_monivetobet bet on bet.combination = a.combination and bet.moniveto_id = a.moniveto_id and bet.list_index = a.list_index
        inner join vakio_monivetoprob b on b.combination=a.match1 and b.moniveto_id = a.moniveto_id and b.list_index = a.list_index
        inner join vakio_monivetoprob c on c.combination=a.match2 and c.moniveto_id = a.moniveto_id and c.list_index = a.list_index
        inner join vakio_monivetoprob d on d.combination=a.match3 and d.moniveto_id = a.moniveto_id and d.list_index = a.list_index
        inner join vakio_monivetoprob e on e.combination=a.match4 and e.moniveto_id = a.moniveto_id and e.list_index = a.list_index
        where bet.bet is null and a.moniveto_id = {params["id"]} and a.list_index = {params["listIndex"]}
        order by share desc
        """
    elif m == 3:
        logging.info("Moniveto 3 match")
        query = f"""
                select a.id, a.combination,
                (a.value * 0.01) * (b.prob * c.prob * d.prob) as yield, bet.bet,
                (b.prob * c.prob * d.prob) as prob, 
                a.value * 0.01 * {line_cost} as win,
                ((a.value * 0.01) * (b.prob * c.prob * d.prob) - 1) / (a.value * 0.01) * 1000 as share
                from vakio_monivetoodds a 
                left join vakio_monivetobet bet on (bet.combination = a.combination and bet.moniveto_id = a.moniveto_id and bet.list_index = a.list_index)
                inner join vakio_monivetoprob b on b.combination=a.match1 and b.moniveto_id = a.moniveto_id and b.list_index = a.list_index
                inner join vakio_monivetoprob c on c.combination=a.match2 and c.moniveto_id = a.moniveto_id and c.list_index = a.list_index
                inner join vakio_monivetoprob d on d.combination=a.match3 and d.moniveto_id = a.moniveto_id and d.list_index = a.list_index
                where bet.bet is null and a.moniveto_id = {params["id"]} and a.list_index = {params["listIndex"]}
                order by share desc
                """
    else:
        query = f"""
                    select a.id, a.combination,
                    (a.value * 0.01) * (b.prob * c.prob) as yield, bet.bet,
                    (b.prob * c.prob) as prob, 
                    a.value * 0.01 * {line_cost} as win,
                    ((a.value * 0.01) * (b.prob * c.prob) - 1) / (a.value * 0.01) * 1000 as share
                    from vakio_monivetoodds a 
                    left join vakio_monivetobet bet on (bet.combination = a.combination and bet.moniveto_id = a.moniveto_id and bet.list_index = a.list_index)
                    inner join vakio_monivetoprob b on b.combination=a.match1 and b.moniveto_id = a.moniveto_id and b.list_index = a.list_index
                    inner join vakio_monivetoprob c on c.combination=a.match2 and c.moniveto_id = a.moniveto_id and c.list_index = a.list_index
                    where bet.bet is null and a.moniveto_id = {params["id"]} and a.list_index = {params["listIndex"]}
                    order by share desc
                    """
    data = MonivetoOdds.objects.raw(query)

    data = pd.DataFrame([item.__dict__ for item in data])
    columns = ['combination', 'prob',  'yield', 'win', 'share', 'bet']
    if len(data) == 0:
        logging.info("No data to bet")
        exit(0)
    yield_limit = 1.8
    df = data[data['yield'] > yield_limit]
    df = df[columns]

    logging.info(
        f"DataFrame:\n{tabulate(df.head(80), headers='keys', tablefmt='psql', showindex=False)}")
    logging.info("Profitable lines:" + str(len(df)) + " of " + str(len(data)) + ' ' + str(round((len(df)/len(data)*100),2)) + "%")
    logging.info("Yield limit:" + str(yield_limit))

    max_bet = int(max_bet_eur / line_cost)
    df = df.head(max_bet)
    logging.info("Lines to bet: " + str(len(df)) + " with " + str(max_bet) + " max bet")
    end = datetime.now()
    scores = {}
    for index, row in df.iterrows():
        match_scores = row['combination'].split(",")
        for i, score in enumerate(match_scores):
            if str(i) not in scores:
                scores[str(i)] = {}
            if score not in scores[str(i)]:
                scores[str(i)][score] = 1
            else:
                scores[str(i)][score] += 1

    # Sort each match's values from biggest to smallest and place into a new dictionary
    sorted_matches = {
        match: dict(sorted(score.items(), key=lambda item: item[1], reverse=True))
        for match, score in scores.items()
    }

    # Using logging to output the result
    logging.info("Sorted Matches:")
    i = 0
    for match, scores in sorted_matches.items():
        if i == 0:
            logging.info(f"{qs.home1} - {qs.away1}: {scores}")
        elif i == 1:
            logging.info(f"{qs.home2} - {qs.away2}: {scores}")
        elif i == 2:
            logging.info(f"{qs.home3} - {qs.away3}: {scores}")
        else:
            logging.info(f"{qs.home4} - {qs.away4}: {scores}")
        i += 1
    logging.info('Script ended')
    logging.info('Time elapsed: {}'.format(end - start))
    if bet != 'bet':
        exit()
    session = login(params["username"], params["password"])
    bankroll = get_balance(session)
    for index, row in df.iterrows():
        line = row['combination'].split(',')
        # Data for wager
        data = create_multiscore_wager(params["listIndex"], stake, line)
        data['selections'] = data["boards"][0]["selections"]
        matches = json.dumps(data)
        winshare = get_sport_winshare(params["id"], matches)
        bet_limit = row["prob"]*winshare
        if bet_limit < 1.0:
            logging.info("Bet limit too low: %s" % bet_limit)
            continue
        is_bet_placed = place_wagers(data, session)
        balance = get_balance(session)
        if balance < 0.0:
            break
        if balance < bankroll and is_bet_placed:
            logging.info("Line: %s, winshare: %.2f, balance: %.2f" % (row['combination'], winshare*0.01*line_cost, balance / 100.0))
            try:
                bet = MonivetoOdds.objects.update_or_create(
                    combination=row["combination"],
                    moniveto_id=moniveto_id,
                    list_index=list_index,
                    defaults={
                        "bet": True,
                    }
                )
                MonivetoBet.objects.create(
                    combination=row["combination"],
                    moniveto_id=moniveto_id,
                    list_index=list_index,
                    bet=True,
                    value=winshare,
                )
                bankroll = balance
            except Exception as e:
                logging.error(e)
                continue