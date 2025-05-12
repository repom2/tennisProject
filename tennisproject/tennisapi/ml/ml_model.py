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
from tennisapi.ml.balance_data import balance_train_data
from tennisapi.ml.features import features
from tennisapi.ml.match_data import get_data

warnings.filterwarnings("ignore")


def classifier(
    x_train,
    y_train,
    features,
    round_mapping,
):
    scaler = ColumnTransformer(
        remainder="passthrough",  # passthough features not listed
        transformers=[
            (
                "num_preprocess",
                MinMaxScaler(),
                [
                    "loser_hard_elo",
                    "winner_hard_elo",
                    "loser_games",
                    "winner_games",
                    "winner_year_elo",
                    "loser_year_elo",
                ],
            )
        ],
    )

    classifier = GradientBoostingClassifier(
        n_estimators=1500,
        # learning_rate=0.05,
        # max_depth=6,
        # warm_start=True,
        # validation_fraction=0.1,
    )
    # classifier = LogisticRegression(max_iter=500)
    classifier = LinearRegression()
    # classifier = xgb.XGBClassifier()
    # classifier = RandomForestClassifier(n_estimators=1500)

    pipeline = Pipeline(
        [
            ("preprocessor", scaler),
            ("feature_selection", SelectFromModel(LinearSVC(penalty="l1", dual=False))),
            ("classifier", classifier),
        ]
    )

    # pipeline = make_pipeline(scaler, classifier)
    model = pipeline.fit(x_train, y_train.values.ravel())
    # GradientBoostingClassifier
    # model.feature_importances = model.steps[1][1].feature_importances_
    # LogisticRegression
    model.feature_importances = None  # model.steps[1][1].coef_[0]
    model.feature_names = features
    model.round_mapping = round_mapping

    return model


def train_model():
    data = get_data()

    data = data[data["winner_year_games"] > 1]
    data = data[data["loser_year_games"] > 1]
    data = data[data["loser_hard_elo"] > 1391]
    data = data[data["loser_hard_elo"] < 2195]
    data = data[data["winner_hard_elo"] > 1391]
    data = data[data["winner_hard_elo"] < 2195]
    data = data[data["loser_games"] > 1]
    data = data[data["winner_games"] > 1]

    feature = features()

    f = feature + ["result"] + ["date", "winner_name", "loser_name"]
    data = data[f]
    data = data.dropna()
    data, round_mapping = balance_train_data(data)
    x_train = data[feature]
    print("Lenght of Train Data:", len(x_train))
    y_train = data[["result"]]

    model = classifier(
        x_train,
        y_train,
        feature,
        round_mapping,
    )

    local_path = os.getcwd() + "/tennisapi/ml/trained_models/"

    file_name = "test"
    file_path = local_path + file_name
    joblib.dump(model, file_path)
