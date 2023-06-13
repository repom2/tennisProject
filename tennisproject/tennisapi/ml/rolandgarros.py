import warnings

import pandas as pd
from django.db import connection
import os

import joblib
import pandas as pd
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (GradientBoostingClassifier,
                              RandomForestClassifier, RandomForestRegressor)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import (LabelEncoder, MinMaxScaler, Normalizer,
                                   StandardScaler)

warnings.filterwarnings("ignore")


def get_data():
    query = "select \
                date, \
                winner_name, \
                loser_name, \
                round_name, \
                winner_elo + winner_change as winner_elo, \
                winner_hardelo, \
                winner_games, \
                winner_year_games, \
                round(winner_win::numeric / winner_year_games::numeric, 2) as winner_win_percent, \
                loser_elo - loser_change as loser_elo, \
                loser_hardelo, \
                loser_games, \
                loser_year_games, \
                round(loser_win::numeric / loser_year_games::numeric, 2) as loser_win_percent, " \
                "1 as result, " \
                "case when home_court_time is null then 0 else home_court_time / 60 end as home_court_time, \
		        case when away_court_time is null then 0 else away_court_time / 60 end as away_court_time \
            from ( \
            select \
                a.date, \
                h.last_name as winner_name, \
                aw.last_name as loser_name, \
                round_name, \
                (select elo from tennisapi_atpelo el where el.player_id=winner_id and el.match_id=b.id) as winner_elo, " \
                "(select elo from tennisapi_atphardelo el where el.player_id=winner_id and el.date < b.date order by games desc limit 1) as winner_hardelo, \
                (select elo_change from tennisapi_atpelo el where el.player_id=winner_id and el.match_id=b.id) as winner_change, \
                (select count(*) from tennisapi_atpelo c where c.player_id=winner_id and c.date < b.date) as winner_games, \
                (select count(*) from tennisapi_atpelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select elo from tennisapi_atpelo el where el.player_id=loser_id and el.match_id=b.id) as loser_elo, \
                (select elo from tennisapi_atphardelo el where el.player_id=loser_id and el.date < b.date order by games desc limit 1) as loser_hardelo, \
                (select elo_change from tennisapi_atpelo el where el.player_id=loser_id and el.match_id=b.id) as loser_change, \
                (select count(*) from tennisapi_atpelo c where c.player_id=loser_id and c.date < b.date) as loser_games, \
                (select count(*) from tennisapi_atpelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win, " \
                "(select sum(court_time) from tennisapi_atpmatches c " \
                "where a.id=c.tour_id and " \
                "c.match_num < b.match_num and (c.winner_id=b.winner_id or c.loser_id=b.winner_id)) as home_court_time, " \
                "(select sum(court_time) from tennisapi_atpmatches c " \
                "where a.id=c.tour_id and " \
                "c.match_num < b.match_num and (c.winner_id=b.loser_id or c.loser_id=b.loser_id)) as away_court_time " \
            "from tennisapi_atptour a \
            inner join tennisapi_atpmatches b on b.tour_id=a.id \
            left join tennisapi_players h on h.id = b.winner_id \
            left join tennisapi_players aw on aw.id = b.loser_id \
            where name ilike '%garros%' and round_name not ilike 'qualification%'  ) " \
            "ss;"

    df = pd.read_sql(query, connection)

    return df


def train_model(
        df,
        features,
        round_mapping
):
    f = features + ['result']
    df = df[f]
    df = df.dropna()
    x_train = df[features]
    print("Lenght of Train Data:", len(x_train))
    y_train = df[['result']]

    scaler = ColumnTransformer(
        remainder='passthrough',  # passthough features not listed
        transformers=[("num_preprocess", MinMaxScaler(), [
            "loser_elo",
            "winner_elo",
            "loser_games",
            "winner_games",
            "winner_hardelo",
            "loser_hardelo",
        ])]
    )

    classifier = GradientBoostingClassifier(n_estimators=1500)
    #classifier = LogisticRegression(max_iter=500)
    #classifier = LinearRegression()
    #classifier = xgb.XGBClassifier()
    #classifier = RandomForestClassifier(n_estimators=1500)

    pipeline = make_pipeline(scaler, classifier)
    model = pipeline.fit(x_train, y_train.values.ravel())
    # GradientBoostingClassifier
    #model.feature_importances = model.steps[1][1].feature_importances_
    # LogisticRegression
    model.feature_importances = None#model.steps[1][1].coef_[0]
    model.feature_names = features
    model.round_mapping = round_mapping

    return model


def label_round_name(data):
    le = LabelEncoder()
    label = le.fit_transform(data['round_name'])
    name_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    data["round_name"] = label

    return data, name_mapping


def tennis_prediction():
    data = get_data()
    # shuffle the DataFrame rows
    data = data.sample(frac=1)
    print(data)

    df1 = data.iloc[:3478, :]
    df2 = data.iloc[3478:, :]

    columns = [
        'date',
        'winner_name',
        'loser_name',
        'round_name',
        'winner_elo',
        'winner_hardelo',
        'winner_games',
        'winner_year_games',
        'winner_win_percent',
        'home_court_time',
        'loser_elo',
        'loser_hardelo',
        'loser_games',
        'loser_year_games',
        'loser_win_percent',
        'away_court_time',
        'result'
    ]
    revert_columns = [
        'date',
        'winner_name',
        'loser_name',
        'round_name',
        'loser_elo',
        'loser_hardelo',
        'loser_games',
        'loser_year_games',
        'loser_win_percent',
        'away_court_time',
        'winner_elo',
        'winner_hardelo',
        'winner_games',
        'winner_year_games',
        'winner_win_percent',
        'home_court_time',
        'result'
    ]

    df2 = df2[revert_columns]
    df2["result"] = 0
    df2.columns = columns

    merge_df = pd.concat([df1, df2])

    train_data, round_mapping = label_round_name(merge_df)

    print(train_data.head())

    features = [
        'round_name',
        'loser_elo',
        'loser_hardelo',
        'loser_games',
        'loser_year_games',
        'loser_win_percent',
        'away_court_time',
        'winner_elo',
        'winner_hardelo',
        'winner_games',
        'winner_year_games',
        'winner_win_percent',
        'home_court_time',
    ]

    #train_data['home_court_time'] = pd.to_datetime(train_data['home_court_time'], unit='s')
    #train_data['away_court_time'] = pd.to_datetime(train_data['away_court_time'], unit='s')
    #train_data['home_court_time'] = train_data['home_court_time'].dt.strftime('%M')
    #train_data['away_court_time'] = train_data['away_court_time'].dt.strftime('%M')

    model = train_model(
        train_data,
        features,
        round_mapping
    )

    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "roland_garros_atp_model_gbc_hard_time"
    file_path = local_path + file_name
    joblib.dump(model, file_path)
