import pandas as pd
import requests
import json
from sport_wager import create_sport_wager
from ast import literal_eval

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
        winshare["value"], winshare["numberOfBets"], ",".join(board)))



if __name__ == '__main__':
    s = login("repom", "_W14350300n1")
    # read csv to dataframe
    df = pd.read_csv('combinations.csv')
    print(len(df))
    print(df.describe())
    print(df.head())
    print(df.info())

    #print(json.dumps(df.head(2)))

    df = df.head(5)

    df = df['combination'].apply(literal_eval).tolist()

    print(df)

    #get_sport_winshare("55446", g)

    matches = ["1X2", "1X2", "1X2", "1X2", "1X2", "2", "1", "X", "2", "1", "X", "1"]
    print(len(matches))

    data = create_sport_wager("", 0, matches, False)
    print(data)
    data['page'] = 2
    data = json.dumps(data)
    get_sport_winshare("55446", data)