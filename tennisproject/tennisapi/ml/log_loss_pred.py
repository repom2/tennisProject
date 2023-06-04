from numpy import loadtxt
from tensorflow.keras.models import load_model
import psycopg2
from psycopg2 import extras
import pandas as pd
import numpy as np
from tensorflow.keras import backend as K
import warnings

from django.db import connection
import os

import joblib


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
                winner_hardelo, \
                winner_games, \
                winner_year_games, \
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent, \
                loser_elo, \
                loser_hardelo, \
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
                (select elo from tennisapi_wtaelo el where el.player_id=home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_elo, \
                (select elo from tennisapi_wtahardelo el where el.player_id=home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_hardelo, \
                (select count(*) from tennisapi_wtaelo c where c.player_id=home_id and c.date < date(b.start_at)) as winner_games, \
                (select count(*) from tennisapi_wtaelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select elo from tennisapi_wtaelo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_elo,  \
                (select elo from tennisapi_wtahardelo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,  \
                (select count(*) from tennisapi_wtaelo c where c.player_id=away_id and c.date < date(b.start_at)) as loser_games, \
                (select count(*) from tennisapi_wtaelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtaelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtaelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win \
            from tennisapi_wtatour a \
            inner join tennisapi_wtamatch b on b.tour_id=a.id \
            left join tennisapi_wtaplayers h on h.id = b.home_id \
            left join tennisapi_wtaplayers aw on aw.id = b.away_id \
            where name ilike '%garros%' and round_name not ilike 'qualification%' ) " \
            "ss where winner_name is not null and loser_name is not null order by start_at;"

    df = pd.read_sql(query, connection)

    return df


def label_team(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data



def odds_loss(y_true, y_pred):
    """
    The function implements the custom loss function mentioned in info.pdf

    Inputs
    true : a vector of dimension batch_size, 7. A label encoded version of the output and the backp1_a and backp1_b
    pred : a vector of probabilities of dimension batch_size , 5.

    Returns
    the loss value
    """
    win_home = y_true[:, 0:1]

    win_away = y_true[:, 1:2]
    no_bet = y_true[:, 2:3]
    close_home = y_true[:, 3:4]

    close_away = y_true[:, 4:5]
    gain_loss_vector = K.concatenate(
        [win_home * (close_home - 1) + (1 - win_home) * -1 / (close_home - 1),
         # if (1 - win_home) * -1 > 0 else (1 - win_home) * -1 / (close_home - 1)),
         win_away * (close_away - 1) + (1 - win_away) * -1 / (close_away - 1),
         # if (1 - win_away) * -1 > 0 else (1 - win_away) * -1 / (close_away - 1)),
         K.zeros_like(close_home)], axis=1)

    print(gain_loss_vector)
    print(y_pred)
    return -1 * K.mean(K.sum(gain_loss_vector * y_pred, axis=1))


def log_loss_pred():
    data = get_data()
    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "roland_garros_wta_model_gbc"
    file_path = local_path + file_name

    model = joblib.load(file_path)
    features = model.feature_names
    round_mapping = model.round_mapping

    data = label_team(data, round_mapping)

    data = data.dropna()
    x = data[features]
    # print(x.head())

    y_pred = model.predict_proba(x)
    # y_pred = model.predict(x)

    # print(y_pred)

    data['y2'] = y_pred[:, 0]
    data['y1'] = y_pred[:, 1]
    # data['y2'] = y_pred - 1
    # data['y1'] = y_pred
    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)
    data['yield1'] = data['y1'] * data['home_odds']
    data['yield2'] = data['y2'] * data['away_odds']

    i = 0
    '''
    Vector of true labels (Win Home, Win spread home, Win spread away, Win Away, No bet)
    '''
    y_full = []
    x_full = []

    x_test = []

    match_id_list = []

    for nro, row in data.iterrows():
        y = [0, 0, 0, 0, 0]

        x = [
            row.round_name,
            row.winner_elo,
            row.winner_hardelo,
            row.winner_games,
            row.winner_year_games,
            row.winner_win_percent,
            row.loser_elo,
            row.loser_hardelo,
            row.loser_games,
            row.loser_year_games,
            row.loser_win_percent,
            row.home_odds,
            row.away_odds,
            #row["y1"],
            #row["y2"],
            row["yield1"],
            row["yield2"],
        ]

        x = np.asarray(x).astype('float32')
        x_full.append(x)

        x_t = [row.winner_name, row.loser_name, row.home_odds, row.away_odds, row.winner_code, row["yield1"],
            row["yield2"]]
        x_test.append(x_t)

        i += 1

    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "odds_loss.hdf5"
    file_path = local_path + file_name
    model = load_model(file_path, custom_objects={'odds_loss': odds_loss})#, compile=False)
    # summarize model.
    # model.summary()
    # load dataset

    np.set_printoptions(suppress=True)

    samples_to_predict = np.array(x_full)

    # print(samples_to_predict)

    predictions = model.predict(samples_to_predict)
    # print(predictions)

    # Generate arg maxes for predictions
    classes = np.argmax(predictions, axis=1)
    print(classes)
    print(len(x_test))
    #print(x_test)
    print(len(classes))

    zip_obj = zip(x_test, classes)

    bankroll = 1000
    bankroll2 = 1000
    max_bet = 0.05
    roll = 100
    bet = 100
    for row, pred in zip_obj:
        yield1 = row[5]
        yield2 = row[6]
        if pred == 0:
            pred = 1
            bet2 = bankroll2 * max_bet
        elif pred == 1:
            pred = 2
            bet2 = bankroll2 * max_bet
        else:
            pred = 'pass'
            bet2 = bankroll2 * max_bet
        limit = bankroll2 * max_bet
        if bet2 > limit:
            bet2 = limit
        if row[4] == pred:
            if pred == 1:
                bankroll += (row[2] - 1) * 100
                bankroll2 += bet2
            elif pred == 2:
                bankroll += (row[3] - 1) * 100
                bankroll2 += bet2
            else:
                continue
        elif row[4] != pred and pred != 'pass':
            bankroll -= 100
            bankroll2 -= bet2
        else:
            pass
        print(row, pred, bankroll, bankroll2)