import logging
import os
import warnings

import joblib
import pandas as pd
import xgboost as xgb
from django.db import connection
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import MinMaxScaler, Normalizer, StandardScaler
from sklearn.svm import LinearSVC
from tabulate import tabulate
from tennisapi.ml.balance_data import balance_train_data
from tennisapi.ml.features import features
from tennisapi.models import Bet

# Retrieve the root logger
logging = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def get_data_atp_data(params):
    surface = params.get("surface", "hard")
    query = """
        select m.tour_id, m.home_name, m.away_name,
            case when winner_code = 1 then 0 else 1 end as winner_code, 
            b.start_at,
            b.home_odds, b.away_odds,
            elo_prob_hard,
            elo_prob_grass,
            elo_prob_clay,
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
        inner join tennisapi_match m on b.match_id=m.id
        where (winner_code=1 or winner_code=2) 
        and m.surface = '%s'
        """
    df = pd.read_sql(query, connection, params=[surface])

    return df


def get_data_wta_data(params):
    surface = params.get("surface", "hard")
    query = """
        select m.tour_id, m.home_name, m.away_name,
            case when winner_code = 1 then 0 else 1 end as winner_code, 
            b.start_at,
            b.home_odds, b.away_odds,
            elo_prob_hard,
            year_elo_prob,
            elo_prob_grass,
            elo_prob_clay,
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
        inner join tennisapi_wtamatch m on b.match_id=m.id
        where 
        (winner_code=1 or winner_code=2)
        and m.surface = '%s'
        order by b.start_at desc;
        """
    df = pd.read_sql(query, connection, params=[surface])

    return df


def classifier(
    x_train,
    y_train,
    features,
    round_mapping,
):
    if "h2h_win" in features:
        scaler = ColumnTransformer(
            remainder="passthrough",  # passthough features not listed
            transformers=[
                (
                    "num_preprocess",
                    MinMaxScaler(),
                    [
                        "h2h_win",
                    ],
                )
            ],
        )
    else:
        scaler = None
    classifier = LogisticRegression(max_iter=500)
    classifier_rf = RandomForestClassifier(n_estimators=500)

    pipeline = Pipeline(
        [
            ("preprocessor", scaler),
            # ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
            ("classifier", classifier),
        ]
    )
    pipeline_rf = Pipeline(
        [
            ("preprocessor", scaler),
            # ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
            ("classifier", classifier_rf),
        ]
    )

    # pipeline = make_pipeline(scaler, classifier)
    model = pipeline.fit(x_train, y_train.values.ravel())
    model_rf = pipeline_rf.fit(x_train, y_train.values.ravel())
    # GradientBoostingClassifier
    # model.feature_importances = model.steps[1][1].feature_importances_
    # RandomForestClassifier
    model.feature_importances = (
        None  # pipeline.named_steps['classifier'].feature_importances_
    )
    # LogisticRegression
    # model.feature_importances = None#model.steps[1][1].coef_[0]
    model.feature_names = features
    model.round_mapping = round_mapping

    return model, model_rf


def train_ml_model(row, level, params, surface, stats_win_field, elo_prob_field):
    # Ensure params has the surface key
    if isinstance(params, dict):
        params["surface"] = surface
    else:
        params = {"surface": surface}
    logging.info("-" * 50)
    # logging.info(f"Training model for {row['winner_name']} vs {row['loser_name']}")
    home_name = row["winner_fullname"]
    away_name = row["loser_fullname"]
    features = [
        #'home_odds',
        "year_elo_prob",
        # stats_win_field,
        "stats_win",
        elo_prob_field,
        #'fatigue',
        #'h2h_win',
        #'home_fatigue',
        #'away_fatigue',
        #'walkover_home',
        #'walkover_away',
        #'home_inj_score',
        #'away_inj_score',
        #'common_opponents',
        #'round_code',
    ]
    if level == "wta" and surface == "clay":
        features += ["elo_prob_hard"]
    # pandas series to dataframe
    df = row.to_frame().T
    odds_home = df["home_odds"].iloc[0]
    odds_away = df["away_odds"].iloc[0]
    stats_win_home = df[stats_win_field].iloc[0]
    stats_win_away = 1 - stats_win_home
    df["home_odds"] = 1 / df["home_odds"]
    # df['home_fatigue'] = 3
    # df["away_fatigue"] = 0.1
    df["fatigue"] = df["home_fatigue"] - df["away_fatigue"]
    if "fatigue" in features:
        if df["fatigue"].isnull().values.any():
            features.remove("fatigue")
    if "home_fatigue" in features:
        if (
            df["home_fatigue"].isnull().values.any()
            or df["away_fatigue"].isnull().values.any()
        ):
            features.remove("home_fatigue")
            features.remove("away_fatigue")

    if "h2h_win" in features:
        try:
            df["h2h_win"] = (
                df["h2h_win"] * df["h2h_matches"]
                - (1 - df["h2h_win"]) * df["h2h_matches"]
            ).astype(int)
            if df["h2h_win"].iloc[0] == 0:
                features.remove("h2h_win")
        except Exception as e:
            features.remove("h2h_win")
    if "common_opponents" in features:
        if (
            df["common_opponents"].isnull().values.any()
            or df["common_opponents_count"].iloc[0] < 5
        ):
            features.remove("common_opponents")
    if df["year_elo_prob"].isnull().values.any():
        features.remove("year_elo_prob")

    df = df[features]

    if surface == "grass":
        df = df.rename(
            columns={"elo_prob_grass": "elo_prob", "stats_win_grass": "stats_win"}
        )
        # replace from list features value stats_win_grass to stats_win
        features = [w.replace("stats_win_grass", "stats_win") for w in features]
        features = [w.replace("elo_prob_grass", "elo_prob") for w in features]
    if surface == "clay":
        df = df.rename(
            columns={"elo_prob_clay": "elo_prob", "stats_win_clay": "stats_win"}
        )
        # replace from list features value stats_win_grass to stats_win
        features = [w.replace("stats_win_clay", "stats_win") for w in features]
        features = [w.replace("elo_prob_clay", "elo_prob") for w in features]
    elif surface == "hard":
        df = df.rename(columns={"stats_win_hard": "stats_win"})
        # replace from list features value stats_win_grass to stats_win
        features = [w.replace("stats_win_hard", "stats_win") for w in features]

    if level == "atp":
        data = get_data_atp_data(params)
    else:
        data = get_data_wta_data(params)

    if surface == "clay":
        # Replace column name 'elo_prob_clay' with 'elo_prob'
        data = data.rename(
            columns={"elo_prob_clay": "elo_prob", "stats_win_clay": "stats_win"}
        )

    f = features + ["winner_code"] + ["start_at", "home_name", "away_name"]

    try:
        data = data[f]
    except Exception as e:
        logging.error(f"Error: {e}")
        return None, None, None, None
    data_length = len(data)
    data = data.dropna()

    # data, round_mapping = balance_train_data(data)

    x_train = data[features]
    y_train = data[["winner_code"]]

    model_logistic, model_rf = classifier(
        x_train,
        y_train,
        features,
        None,
    )

    title = f"Model for {home_name} vs {away_name}"
    table_str = tabulate(df, headers="keys", tablefmt="psql", showindex=True)
    # Prepend the title to the table string
    log_output = f"{title}\n{table_str}"

    # Log the table with the title
    logging.info("\n" + log_output)

    try:
        y_pred = model_logistic.predict_proba(df)
        y_pred_rf = model_rf.predict_proba(df)
    except ValueError as e:
        logging.error(f"Error: {e}")
        return None, None, None, None

    # log probabilities
    prob_home = round(y_pred[0][0], 3)
    prob_home_rf = round(y_pred_rf[0][0], 3)
    prob_away = round(y_pred[0][1], 3)
    prob_away_rf = round(y_pred_rf[0][1], 3)
    odds_limit_home = round(1 / prob_home, 3)
    odds_limit_away = round(1 / prob_away, 3)

    p_home = df["elo_prob"].iloc[0]
    p_away = 1 - p_home
    try:
        yield_home = round(odds_home * prob_home, 3)
        yield_away = round(odds_away * prob_away, 3)
    except TypeError:
        yield_home = 0
        yield_away = 0

    logging.info(
        f"Probabilities: {prob_home} - {prob_away} Odds: {odds_limit_home}/{odds_limit_away} RF: {prob_home_rf}/{prob_away_rf}"
    )
    logging.info(f"Odds: {odds_home} {odds_away} Yield {yield_home} {yield_away}")

    return prob_home, prob_away, yield_home, yield_away
