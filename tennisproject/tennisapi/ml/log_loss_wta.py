import warnings

import pandas as pd
from django.db import connection
import os

import joblib

import numpy as np

from tensorflow.keras.layers import BatchNormalization, Dense, Input, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
#import matplotlib.pyplot as plt
#from sklearn.preprocessing import StandardScaler, MinMaxScaler
from numpy import asarray
from sklearn.preprocessing import (LabelEncoder, MinMaxScaler, Normalizer,
                                   StandardScaler)


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000000)

warnings.filterwarnings("ignore")

pd.set_option('display.max_rows', 600)


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
                (select count(*) from tennisapi_wtaelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_games, \
                (select elo from tennisapi_wtaelo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_elo,  \
                (select elo from tennisapi_wtahardelo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,  \
                (select count(*) from tennisapi_wtaelo c where c.player_id=away_id and c.date < date(b.start_at)) as loser_games, \
                (select count(*) from tennisapi_wtaelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtaelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtaelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_win \
            from tennisapi_wtamatchrolandg b \
            left join tennisapi_wtaplayers h on h.id = b.home_id \
            left join tennisapi_wtaplayers aw on aw.id = b.away_id \
            where round_name not ilike 'qualification%' ) " \
            "ss where winner_name is not null and loser_name is not null and home_odds is not null and away_odds is not null order by start_at;"

    df = pd.read_sql(query, connection)

    return df


def get_model(input_dim, output_dim, base=1000, multiplier=0.25, p=0.2):
    inputs = Input(shape=(input_dim,))
    l = BatchNormalization()(inputs)
    l = Dropout(p)(l)
    n = base
    l = Dense(n, activation='relu')(l)
    l = BatchNormalization()(l)
    l = Dropout(p)(l)
    n = int(n * multiplier)
    l = Dense(n, activation='relu')(l)
    l = BatchNormalization()(l)
    l = Dropout(p)(l)
    n = int(n * multiplier)
    l = Dense(n, activation='relu')(l)

    outputs = Dense(output_dim, activation='softmax')(l)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='Nadam', loss=odds_loss)
    return model


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
    print(win_away)
    no_bet = y_true[:, 2:3]
    close_home = y_true[:, 3:4]

    close_away = y_true[:, 4:5]
    """negative_home = (1 - win_home) * -1
    negative_away = (1 - win_away) * -1
    if negative_home < 0:
        negative_home = negative_home / (close_home - 1)
    
    if negative_away < 0:
        negative_away = negative_away / (close_away - 1)"""
    gain_loss_vector = K.concatenate(
        [win_home * (close_home - 1) + (1 - win_home) * -1/ (close_home - 1), #if (1 - win_home) * -1 > 0 else (1 - win_home) * -1 / (close_home - 1)),
        win_away * (close_away - 1) + (1 - win_away) * -1/ (close_away - 1), #if (1 - win_away) * -1 > 0 else (1 - win_away) * -1 / (close_away - 1)),
        K.zeros_like(close_home)], axis=1)
    print(gain_loss_vector)
    print(y_pred)
    return -1 * K.mean(K.sum(gain_loss_vector * y_pred, axis=1))


def label_team(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data


def log_loss_wta():
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

    match_id_list = []

    for nro, row in data.iterrows():
        y = [0, 0, 0]

        result = float(row.winner_code)
        if result == 1:
            y[0] = 1
        elif result == 2:
            y[1] = 1
        else:
            continue

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
            row["y1"],
            row["y2"],
            #row["yield1"],
            #row["yield2"],
        ]

        y += [float(row.home_odds), float(row.away_odds)]

        x = np.asarray(x).astype('float32')
        x_full.append(x)

        y = np.asarray(y).astype('float32')
        y_full.append(y)
        i += 1

    # standardize dataset
    x_full = asarray(x_full)
    y_full = asarray(y_full)
    #scaler = MinMaxScaler()
    #x_full = scaler.fit_transform(x_full)
    #y_full = scaler.fit_transform(y_full)

    print(x_full)
    print(y_full)

    features = [
        'round_name',
        'winner_elo',
        'winner_hardelo',
        'winner_games',
        'winner_year_games',
        'winner_win_percent',
        'loser_elo',
        'loser_hardelo',
        'loser_games',
        'loser_year_games',
        'loser_win_percent',
        'home_odds',
        'away_odds',
        'y1',
        'y2',
        #'yield1',
        #'yield2',
    ]

    y_df = pd.DataFrame(y_full, columns=['home_win', 'away_win', 'even', 'close_home',
                                         'close_away'])
    x_df = pd.DataFrame(x_full, columns=[
        features

    ])

    # features = ['home_odds', 'away_odds', 'lin', 'lin2', 'dr', 'dr2']
    # x_df =x_df[features]

    train_x, test_x, train_y, test_y = train_test_split(x_df, y_df, test_size=0.5)
    #train_x = x_df
    #test_x = x_df
    #train_y = y_df
    #test_y = y_df

    model = get_model(15, 3, 1000, 0.9, 0.7)

    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "odds_loss.hdf5"
    file_path = local_path + file_name

    history = model.fit(train_x, train_y, validation_data=(test_x, test_y),
                        epochs=200, batch_size=25,
                        callbacks=[EarlyStopping(patience=0),
                                   ModelCheckpoint(file_path,
                                                   save_best_only=True,
                                                   save_format='tf')])

    print('Training Loss : {}\nValidation Loss : {}'.format(
        model.evaluate(train_x, train_y),
        model.evaluate(test_x, test_y)))
    print(i)
