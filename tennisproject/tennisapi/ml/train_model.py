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
from tennisapi.ml.balance_data import balance_train_data
from tennisapi.models import Bet
import logging
from tabulate import tabulate

# Retrieve the root logger
logging = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def get_data_atp_data(params):
    query = \
        """
        select m.tour_id, home_name, away_name, 
            case when winner_code = 1 then 0 else 1 end as winner_code, 
            b.start_at,
            b.home_odds, b.away_odds,
            elo_prob,
            year_elo_prob,
            stats_win,
            home_fatigue - away_fatigue as fatigue,
            (round(h2h_win::numeric * h2h_matches, 0) - round((1-h2h_win)::numeric * h2h_matches, 0))::integer as h2h_win,
            case when walkover_home is null then 0 when walkover_home = false then 0 else 1 end as walkover_home,
            case when walkover_away is null then 0 when walkover_away = false then 0 else 1 end as walkover_away,
            home_inj_score,
            away_inj_score,
            common_opponents,
            case when (round_name ilike '%%ifinal%%' or round_name ilike '%%quarterfi%%') then 0
                when (round_name ilike '%%r32%%' or round_name ilike '%%r16%%')  then 1 
                when (round_name ilike '%%r64%%' or round_name ilike '%%r128%%')  then 2 
            else 3 end as round_code,
            h2h_matches,
            common_opponents_count
        from tennisapi_bet b
        inner join tennisapi_match m on b.match_id=m.id inner join tennisapi_atptour t on m.tour_id=t.id
        where (winner_code=1 or winner_code=2) 
        --and (walkover_home is null or walkover_home is false)
        --and (walkover_away is null or walkover_home is false)
        --and home_inj_score > 20.00
        --and away_inj_score < 20.00
        and surface ilike '%%%(surface)s%%'
        --and (round_name ilike '%%ifinal%%' or round_name ilike '%%quarterfi%%' or round_name ilike '%%r16%%')
        """
    # --( m.tour_id like '%-580' or m.tour_id like '%-7117' );
    df = pd.read_sql(query, connection, params=params)

    return df


def get_data_wta_data():
    query = \
        """
        select m.tour_id, home_name, away_name, 
            case when winner_code = 1 then 0 else 1 end as winner_code, 
            b.start_at,
            b.home_odds, b.away_odds,
            elo_prob,
            year_elo_prob,
            stats_win,
            home_fatigue - away_fatigue as fatigue,
            home_fatigue,
            away_fatigue,
            (round(h2h_win::numeric * h2h_matches, 0) - round((1-h2h_win)::numeric * h2h_matches, 0))::integer as h2h_win,
            case when walkover_home is null then 0 when walkover_home = false then 0 else 1 end as walkover_home,
            case when walkover_away is null then 0 when walkover_away = false then 0 else 1 end as walkover_away,
            home_inj_score,
            away_inj_score,
            common_opponents,
            case when (round_name ilike '%ifinal%' or round_name ilike '%quarterfi%') then 0
                when (round_name ilike '%r32%' or round_name ilike '%r16%')  then 1 
                when (round_name ilike '%r64%' or round_name ilike '%r128%')  then 2 
            else 3 end as round_code,
            h2h_matches,
            common_opponents_count
        from tennisapi_betwta b
        inner join tennisapi_wtamatch m on b.match_id=m.id  inner join tennisapi_wtatour t on m.tour_id=t.id
        where 
        --( m.tour_id like '%-580' or m.tour_id like '%-6878' ) and 
        (winner_code=1 or winner_code=2)
        and surface ilike 'Hard'
        --and (walkover_home is null or walkover_home is false)
        --and (walkover_away is null or walkover_home is false)
        order by b.start_at desc;
        """
    df = pd.read_sql(query, connection)#, params=params)

    return df


def classifier(
        x_train,
        y_train,
        features,
        round_mapping,
):
    if "h2h_win" in features:
        scaler = ColumnTransformer(
            remainder='passthrough',  # passthough features not listed
            transformers=[("num_preprocess", MinMaxScaler(), [
                "h2h_win",
            ])]
        )
    else:
        scaler = None
    classifier = LogisticRegression(max_iter=500)
    classifier_rf = RandomForestClassifier(n_estimators=500)

    pipeline = Pipeline([
        ('preprocessor', scaler),
        #('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
        ('classifier', classifier)
    ])
    pipeline_rf = Pipeline([
        ('preprocessor', scaler),
        # ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
        ('classifier', classifier_rf)
    ])

    #pipeline = make_pipeline(scaler, classifier)
    model = pipeline.fit(x_train, y_train.values.ravel())
    model_rf = pipeline_rf.fit(x_train, y_train.values.ravel())
    # GradientBoostingClassifier
    #model.feature_importances = model.steps[1][1].feature_importances_
    # RandomForestClassifier
    model.feature_importances = None#pipeline.named_steps['classifier'].feature_importances_
    # LogisticRegression
    #model.feature_importances = None#model.steps[1][1].coef_[0]
    model.feature_names = features
    model.round_mapping = round_mapping

    return model, model_rf


def train_ml_model(row, level, params):
    logging.info("-" * 50)
    # logging.info(f"Training model for {row['winner_name']} vs {row['loser_name']}")
    home_name = row['winner_fullname']
    away_name = row['loser_fullname']
    features = [
        #'home_odds',
        'elo_prob',
        'year_elo_prob',
        'stats_win',
        'fatigue',
        'h2h_win',
        #'home_fatigue',
        #'away_fatigue',
        #'walkover_home',
        #'walkover_away',
        #'home_inj_score',
        #'away_inj_score',
        'common_opponents',
        #'round_code',
    ]

    # pandas series to dataframe
    df = row.to_frame().T
    odds_home = df['home_odds'].iloc[0]
    odds_away = df['away_odds'].iloc[0]
    df["home_odds"] = 1 / df['home_odds']
    #df['home_fatigue'] = 3
    #df["away_fatigue"] = 0.1
    df["fatigue"] = df['home_fatigue'] - df['away_fatigue']
    if "fatigue" in features:
        if df["fatigue"].isnull().values.any():
            features.remove("fatigue")
    if "home_fatigue" in features:
        if df["home_fatigue"].isnull().values.any() or df["away_fatigue"].isnull().values.any():
            features.remove("home_fatigue")
            features.remove("away_fatigue")

    if "h2h_win" in features:
        try:
            df["h2h_win"] = (df['h2h_win'] * df['h2h_matches'] - (1 - df['h2h_win']) * df['h2h_matches']).astype(int)
            if df["h2h_win"].iloc[0] == 0:
                features.remove("h2h_win")
        except Exception as e:
            features.remove("h2h_win")
    if "common_opponents" in features:
        if df['common_opponents'].isnull().values.any() or df['common_opponents_count'].iloc[0] < 2:
            features.remove("common_opponents")
    if df['year_elo_prob'].isnull().values.any():
        features.remove("year_elo_prob")

    df = df[features]

    if level == 'atp':
        data = get_data_atp_data(params)
    else:
        data = get_data_wta_data()

    #data["home_odds"] = 1/ data['home_odds']

    #data = data[data['h2h_matches'] > 1]
    #data = data[data['common_opponents_count'] > 1]

    f = features + ['winner_code'] + ['start_at', 'home_name', 'away_name']

    data = data[f]
    data_length = len(data)
    data = data.dropna()
    """logging.info(f"Lenght of Data All:{data_length} "
                 f"Home:{len(data[data['winner_code'] == 0])} "
                 f"Away:{len(data[data['winner_code'] == 1])}")"""

    #data, round_mapping = balance_train_data(data)

    x_train = data[features]
    y_train = data[['winner_code']]

    model_logistic, model_rf = classifier(
        x_train,
        y_train,
        features,
        None,
    )

    title = f"Model for {home_name} vs {away_name}"
    table_str = tabulate(df, headers='keys', tablefmt='psql', showindex=True)
    # Prepend the title to the table string
    log_output = f"{title}\n{table_str}"

    # Log the table with the title
    logging.info("\n" + log_output)
    y_pred = model_logistic.predict_proba(df)
    y_pred_rf = model_rf.predict_proba(df)

    # log probabilities
    prob_home = round(y_pred[0][0], 3)
    prob_home_rf = round(y_pred_rf[0][0], 3)
    prob_away = round(y_pred[0][1], 3)
    prob_away_rf = round(y_pred_rf[0][1], 3)
    odds_limit_home = round(1/prob_home, 3)
    odds_limit_away = round(1/prob_away, 3)
    yield_home = round(odds_home * prob_home, 3)
    yield_away = round(odds_away * prob_away, 3)

    logging.info(f"Probabilities: {prob_home} - {prob_away} Odds: {odds_limit_home}/{odds_limit_away} RF: {prob_home_rf}/{prob_away_rf}")
    logging.info(f"Odds: {odds_home} {odds_away} Yield {yield_home} {yield_away}")

    #local_path = os.getcwd() + '/tennisapi/ml/models/'
    #file_name = "test"
    #file_path = local_path + file_name
    #joblib.dump(model, file_path)
    return prob_home, prob_away, yield_home, yield_away
