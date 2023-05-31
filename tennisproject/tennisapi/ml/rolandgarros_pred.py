import warnings

import pandas as pd
from django.db import connection
import os

import joblib
import pandas as pd

warnings.filterwarnings("ignore")


def get_data():
    query = "select \
                start_at, \
                winner_name, \
                loser_name, \
                home_odds, \
                away_odds, \
                round_name, \
                winner_elo, \
                winner_games, \
                winner_year_games, \
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent, \
                loser_elo, \
                loser_games, \
                loser_year_games, \
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent, " \
                "case when winner_code = null then 10 else winner_code end " \
            "from ( \
            select \
                b.start_at, \
                home_odds, \
                away_odds, \
                h.last_name as winner_name, \
                aw.last_name as loser_name, \
                round_name, \
                winner_code, \
                (select elo from tennisapi_atpelo el where el.player_id=home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_elo, \
                (select count(*) from tennisapi_atpelo c where c.player_id=home_id and c.date < date(b.start_at)) as winner_games, \
                (select count(*) from tennisapi_atpelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select elo from tennisapi_atpelo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_elo, " \
                "(select count(*) from tennisapi_atpelo c where c.player_id=away_id and c.date < date(b.start_at)) as loser_games, \
                (select count(*) from tennisapi_atpelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win \
            from tennisapi_atptour a \
            inner join tennisapi_match b on b.tour_id=a.id \
            left join tennisapi_players h on h.id = b.home_id \
            left join tennisapi_players aw on aw.id = b.away_id \
            where name ilike '%garros%' and round_name not ilike 'qualification%' ) " \
            "ss where winner_name is not null and loser_name is not null order by start_at;"

    df = pd.read_sql(query, connection)

    return df


def label_team(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data


def predict_matches():
    data = get_data()
    print(data)
    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "roland_garros_atp_model"
    file_path = local_path + file_name

    model = joblib.load(file_path)
    features = model.feature_names
    round_mapping = model.round_mapping

    data = label_team(data, round_mapping)
    print(features)

    data = data.dropna()
    x = data[features]
    print(x.head())

    y_pred = model.predict_proba(x)

    print(y_pred)

    data['y2'] = y_pred[:,0]
    data['y1'] = y_pred[:,1]
    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)
    print(data)
    data['yield1'] = data['y1'] * data['home_odds']
    data['yield2'] = data['y2'] * data['away_odds']

    data["bankroll"] = None
    data["bankroll2"] = None
    bankroll = 1000
    bankroll2 = 1000
    max_bet = 0.05
    for index, row in data.iterrows():
        if row["yield1"] > 1:
            bet2 = ((row["yield1"] - 1) / (row.home_odds - 1)) * bankroll2
            limit = bankroll2 * max_bet
            if bet2 > limit:
                bet2 = limit
            if row.winner_code == 2:
                bankroll -= 100
                bankroll2 -= bet2
            elif row.winner_code == 1:
                bankroll += (100 * (row.home_odds - 1))
                bankroll2 += (bet2 * (row.home_odds - 1))
            else:
                continue
        elif row["yield2"] > 1:
            bet2 = ((row["yield2"] - 1) / (row.away_odds - 1)) * bankroll2
            limit = bankroll2 * max_bet
            if bet2 > limit:
                bet2 = limit
            if row.winner_code == 1:
                bankroll -= 100
                bankroll2 -= bet2
            elif row.winner_code == 2:
                bankroll += (100 * (row.away_odds - 1))
                bankroll2 += (bet2 * (row.away_odds - 1))
            else:
                continue
        else:
            continue
        data.loc[index, 'bankroll'] = bankroll
        data.loc[index, 'bankroll2'] = bankroll2

    print(data)
    data.to_csv('rg-atp.csv', index=False)

