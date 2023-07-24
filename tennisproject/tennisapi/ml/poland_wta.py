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
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import (LabelEncoder, MinMaxScaler, Normalizer,
                                   StandardScaler)
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
warnings.filterwarnings("ignore")


def get_data():
    query = "select \
                date, \
                winner_name, \
                loser_name, \
                round_name, \
                winner_grasselo + winner_change as winner_grasselo, \
                winner_hardelo, \
                winner_games, \
                winner_year_games, \
                winner_year_grass_games, \
                round(winner_win::numeric / winner_year_games::numeric, 2) as winner_win_percent, \
                round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) as winner_win_grass_percent, " \
                "case when home_court_time is null then 0 else home_court_time / 60 end as home_court_time, " \
                "winner_clayelo, " \
                "loser_grasselo - loser_change as loser_grasselo, \
                loser_hardelo, \
                loser_games, \
                loser_year_games, \
                loser_year_grass_games, \
                round(loser_win::numeric / loser_year_games::numeric, 2) as loser_win_percent, " \
                    "round(loser_grass_win::numeric / loser_year_grass_games::numeric, 2) as loser_win_grass_percent, " \
                    "case when away_court_time is null then 0 else away_court_time / 60 end as away_court_time," \
                "loser_clayelo, " \
                "1 as result  \
            from ( \
            select \
                a.date, \
                h.last_name as winner_name, \
                aw.last_name as loser_name, \
                round_name, \
                (select elo from tennisapi_wtagrasselo el where el.player_id=winner_id and el.match_id=b.id) as winner_grasselo, " \
                "(select elo from tennisapi_wtahardelo el where el.player_id=winner_id and el.date < b.date order by games desc limit 1) as winner_hardelo, \
                (select elo from tennisapi_wtaelo el where el.player_id=winner_id and el.date < b.date order by games desc limit 1) as winner_clayelo, \
                (select elo_change from tennisapi_wtagrasselo el where el.player_id=winner_id and el.match_id=b.id) as winner_change, \
                (select count(*) from tennisapi_wtahardelo c where c.player_id=winner_id and c.date < b.date) as winner_games, \
                (select count(*) from tennisapi_wtahardelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select count(*) from tennisapi_wtahardelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_grass_games, \
                (select elo from tennisapi_wtagrasselo el where el.player_id=loser_id and el.match_id=b.id) as loser_grasselo, \
                (select elo from tennisapi_wtahardelo el where el.player_id=loser_id and el.date < b.date order by games desc limit 1) as loser_hardelo, \
                (select elo from tennisapi_wtaelo el where el.player_id=loser_id and el.date < b.date order by games desc limit 1) as loser_clayelo, \
                (select elo_change from tennisapi_wtagrasselo el where el.player_id=loser_id and el.match_id=b.id) as loser_change, \
                (select count(*) from tennisapi_wtahardelo c where c.player_id=loser_id and c.date < b.date) as loser_games, \
                (select count(*) from tennisapi_wtahardelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select count(*) from tennisapi_wtahardelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_grass_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtahardelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                from tennisapi_wtahardelo c \
                inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_grass_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtahardelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win, " \
                "(select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtahardelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_grass_win, " \
                "(select sum(court_time) from tennisapi_wtamatches c " \
                "where a.id=c.tour_id and " \
                "c.match_num < b.match_num and (c.winner_id=b.winner_id or c.loser_id=b.winner_id)) as home_court_time, " \
                "(select sum(court_time) from tennisapi_wtamatches c " \
                "where a.id=c.tour_id and " \
                "c.match_num < b.match_num and (c.winner_id=b.loser_id or c.loser_id=b.loser_id)) as away_court_time " \
            "from tennisapi_wtatour a \
            inner join tennisapi_wtamatches b on b.tour_id=a.id \
            left join tennisapi_wtaplayers h on h.id = b.winner_id \
            left join tennisapi_wtaplayers aw on aw.id = b.loser_id \
            where surface ilike '%hard%' " \
            " and (" \
            "name ilike '%prague%' " \
            "or name ilike '%washington%' " \
            "or name ilike '%san%jose%' ) "  \
            " and a.date > '2000-1-1' ) " \
            "ss;"

    df = pd.read_sql(query, connection)

    return df


def balance_train_data(data):
    # shuffle the DataFrame rows
    data = data.sample(frac=1)
    l = int(round(len(data.index) / 2, 0))
    print("split", l)
    df1 = data.iloc[:l, :]
    df2 = data.iloc[l:, :]

    # Dont change because have to match with sql
    columns = [
        'date',
        'winner_name',
        'loser_name',
        'round_name',
        'winner_grasselo',
        'winner_hardelo',
        'winner_games',
        'winner_year_games',
        'winner_year_grass_games',
        'winner_win_percent',
        'winner_win_grass_percent',
        'home_court_time',
        'winner_clayelo',
        'loser_grasselo',
        'loser_hardelo',
        'loser_games',
        'loser_year_games',
        'loser_year_grass_games',
        'loser_win_percent',
        'loser_win_grass_percent',
        'away_court_time',
        'loser_clayelo',
        'result'
    ]
    revert_columns = [
        'date',
        'winner_name',
        'loser_name',
        'round_name',
        'loser_grasselo',
        'loser_hardelo',
        'loser_games',
        'loser_year_games',
        'loser_year_grass_games',
        'loser_win_percent',
        'loser_win_grass_percent',
        'away_court_time',
        'loser_clayelo',
        'winner_grasselo',
        'winner_hardelo',
        'winner_games',
        'winner_year_games',
        'winner_year_grass_games',
        'winner_win_percent',
        'winner_win_grass_percent',
        'home_court_time',
        'winner_clayelo',
        'result'
    ]

    df2 = df2[revert_columns]
    df2["result"] = 0
    df2.columns = columns

    merge_df = pd.concat([df1, df2])

    train_data, round_mapping = label_round_name(merge_df)

    print(train_data.head())

    return train_data, round_mapping


def train_model(
        df,
        features,
):
    f = features + ['result'] + ['date', 'winner_name', 'loser_name']
    df = df[f]
    df = df.dropna()
    df, round_mapping = balance_train_data(df)
    x_train = df[features]
    print("Lenght of Train Data:", len(x_train))
    y_train = df[['result']]

    scaler = ColumnTransformer(
        remainder='passthrough',  # passthough features not listed
        transformers=[("num_preprocess", MinMaxScaler(), [
            "loser_hardelo",
            "winner_hardelo",
            "loser_games",
            "winner_games",
            "winner_grasselo",
            "loser_grasselo",
            "winner_clayelo",
            "loser_clayelo",
        ])]
    )

    classifier = GradientBoostingClassifier(
        n_estimators=6500,
        #learning_rate=0.035,
        #max_depth=5,
        #warm_start=True,
        #validation_fraction=0.2,
    )
    #
    classifier = LogisticRegression(max_iter=7500)
    #classifier = LinearRegression()
    #classifier = xgb.XGBClassifier()
    #classifier = RandomForestClassifier(n_estimators=4500)#, max_depth=5)

    #pipeline = make_pipeline(scaler, classifier)
    pipeline = Pipeline([
        ('preprocessor', scaler),
        ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
        ('classifier', classifier)
    ])
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


def poland_wta():
    data = get_data()

    features = [
        'round_name',
        'loser_hardelo',
        'loser_grasselo',
        'loser_games',
        'loser_year_games',
        'loser_year_grass_games',
        'loser_win_percent',
        'loser_win_grass_percent',
        'away_court_time',
        'loser_clayelo',
        'winner_hardelo',
        'winner_grasselo',
        'winner_games',
        'winner_year_games',
        'winner_year_grass_games',
        'winner_win_percent',
        'winner_win_grass_percent',
        'home_court_time',
        'winner_clayelo',
    ]

    model = train_model(
        data,
        features,
    )

    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "poland_wta"
    file_path = local_path + file_name
    joblib.dump(model, file_path)
