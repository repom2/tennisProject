import warnings

import pandas as pd
from django.db import connection
import os

import joblib
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (GradientBoostingClassifier,
                              RandomForestClassifier, RandomForestRegressor)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import (
    MinMaxScaler,
    Normalizer,
    StandardScaler
)
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from tennisapi.ml.features import features
from tennisapi.ml.predict import probability_of_winning
from tennisapi.ml.balance_data import balance_train_data
from tennisapi.models import Bet
import logging
from tabulate import tabulate

# Retrieve the root logger
logging = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def get_train_data(params):
    query = \
        """
            select 
                home_team_id,
                away_team_id,
                b.start_at,
                b.id as match_id,
                home_odds,
                draw_odds,
                away_odds,
                h.name as home_name,
                aw.name as away_name,
                winner_code,
                (select elo from %(elo_table)s elo where elo.team_id=home_team_id and elo.date < date(b.start_at) order by games desc limit 1) as home_elo,
                (select elo from %(elo_table)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as away_elo,
                (select elo from %(elo_home)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_home,
                (select elo from %(elo_away)s elo where elo.team_id=away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_away
            from %(match_table)s b
            left join footballapi_teams h on h.id = b.home_team_id
            left join footballapi_teams aw on aw.id = b.away_team_id
            where (winner_code=1 or winner_code=2 or winner_code=3)
            order by start_at
        """
    df = pd.read_sql(query, connection, params=params)

    return df


def classifier(
        x_train,
        y_train,
        features,
        round_mapping,
):

    classifier = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
    # classifier = RandomForestClassifier(n_estimators=1000)
    scaler = None
    pipeline = Pipeline([
        ('preprocessor', scaler),
        #('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
        ('classifier', classifier)
    ])

    #pipeline = make_pipeline(scaler, classifier)
    model = pipeline.fit(x_train, y_train.values.ravel())
    # GradientBoostingClassifier
    #model.feature_importances = model.steps[1][1].feature_importances_
    # RandomForestClassifier
    model.feature_importances = None#pipeline.named_steps['classifier'].feature_importances_
    # LogisticRegression
    #model.feature_importances = None#model.steps[1][1].coef_[0]
    model.feature_names = features
    model.round_mapping = round_mapping

    return model


def train_ml_model(row, level, params):
    logging.info(f"Training model for {row['home_name']} vs {row['away_name']}")
    features = [
        #'home_odds',
        'elo_prob',
        'elo_prob_home',
    ]

    # pandas series to dataframe
    match_data = row.to_frame().T

    #df["home_odds"] = 1 / df['home_odds']

    df = match_data[features]

    data = get_train_data(params)

    data['elo_prob'] = data['home_elo'] - data['away_elo']
    data['elo_prob_home'] = data['elo_home'] - data['elo_away']
    data['elo_prob'] = data['elo_prob'].apply(probability_of_winning).round(2)
    data['elo_prob_home'] = data['elo_prob_home'].apply(probability_of_winning).round(2)

    data["home_odds"] = 1/ data['home_odds']

    #data = data[data['h2h_matches'] > 1]
    #data = data[data['common_opponents_count'] > 1]

    f = features + ['winner_code'] + ['start_at', 'home_name', 'away_name']

    data = data[f]
    data_length = len(data)
    data = data.dropna()
    logging.info(f"Lenght of Data All:{data_length} "
                 f"Lenght of Home:{len(data[data['winner_code'] == 1])} "
                 f"Lenght of Away:{len(data[data['winner_code'] == 2])}"
                 f"Lenght of Away:{len(data[data['winner_code'] == 3])}"
                 )

    #data, round_mapping = balance_train_data(data)

    x_train = data[features]
    y_train = data[['winner_code']]

    model = classifier(
        x_train,
        y_train,
        features,
        None,
    )

    local_path = os.getcwd() + '/tennisapi/ml/models/'

    logging.info(
    f"DataFrame:\n{tabulate(df, headers='keys', tablefmt='psql', showindex=True)}")
    y_pred = model.predict(df)
    logging.info(f"Predicted: {y_pred}")
    # log probabilities
    logging.info(f""
                 f"Probabilities: 1:{round(model.predict_proba(df)[0][0] , 3)}"
                 f" X:{round(model.predict_proba(df)[0][2] , 3)}"
                 f" 2:{round(model.predict_proba(df)[0][1] , 3)}"
                 f"")
    logging.info(f"Odds: {round(1/match_data['home_odds'].values[0], 2)}:{round(1/match_data['draw_odds'].values[0], 2)}:{round(1/match_data['away_odds'].values[0], 2)}")
    file_name = "test"
    file_path = local_path + file_name
    joblib.dump(model, file_path)
