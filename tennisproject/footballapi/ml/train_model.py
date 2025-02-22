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
from psycopg2.extensions import AsIs
from footballapi.stats.estimated_goals import estimated_goals
from footballapi.stats.poisson import calculate_poisson
import numpy as np

# Retrieve the root logger
logging = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def get_train_data(params, league_avg_home_goals, league_avg_away_goals):
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
                (select avg(home_score) from %(match_table)s l where l.home_team_id=b.home_team_id and l.start_at < date(b.start_at)) as home_goals,
				(select avg(away_score) from %(match_table)s l where l.home_team_id=b.home_team_id and l.start_at < date(b.start_at)) as home_conceded,
				(select avg(away_score) from %(match_table)s l where l.away_team_id=b.away_team_id and l.start_at < date(b.start_at)) as away_goals,
				(select avg(home_score) from %(match_table)s l where l.away_team_id=b.away_team_id and l.start_at < date(b.start_at)) as away_conceded,
                (select elo from %(elo_table)s elo where elo.team_id=b.home_team_id and elo.date < date(b.start_at) order by games desc limit 1) as home_elo,
                (select elo from %(elo_table)s elo where elo.team_id=b.away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as away_elo,
                (select elo from %(elo_home)s elo where elo.team_id=b.away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_home,
                (select elo from %(elo_away)s elo where elo.team_id=b.away_team_id and elo.date < date(b.start_at) order by games desc limit 1) as elo_away
            from %(match_table)s b
            left join footballapi_teams h on h.id = b.home_team_id
            left join footballapi_teams aw on aw.id = b.away_team_id
            where (winner_code=1 or winner_code=2 or winner_code=3)
            order by start_at
        """
    df = pd.read_sql(query, connection, params=params)

    df[['home_est_goals', 'away_est_goals']] = pd.DataFrame(
        np.row_stack(
            np.vectorize(estimated_goals, otypes=['O'])(
                league_avg_home_goals['home_goals'],
                league_avg_away_goals['away_goals'],
                df['home_goals'],
                df['home_conceded'],
                df['away_goals'],
                df['away_conceded']
            )
        ), index=df.index)

    df[['home_poisson', 'draw_poisson', 'away_poisson']] = pd.DataFrame(
        np.row_stack(
            np.vectorize(calculate_poisson, otypes=['O'])(
                df['home_est_goals'],
                df['away_est_goals'],
            )
        ), index=df.index)

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


def train_ml_model(row, level, params, league_avg_home_goals, league_avg_away_goals):
    logging.info(f"Training model for {row['home_name']} vs {row['away_name']}")
    home_name = row['home_name']
    away_name = row['away_name']
    odds_home = row['home_odds']
    odds_away = row['away_odds']
    odds_draw = row['draw_odds']
    if odds_home is None or odds_away is None or odds_draw is None:
        logging.info(f"Odds are not available for {home_name} vs {away_name}")
        pass
    features = [
        #'draw_odds',
        #'away_odds',
        #'home_odds',
        'elo_prob',
        #'elo_prob_home',
        'home_poisson',
        'draw_poisson',
        'away_poisson',
    ]

    # pandas series to dataframe
    match_data = row.to_frame().T
    match_data["homeodds"] = 1 / match_data['home_odds']

    df = match_data[features]

    if level == 'facup':
        params['match_table'] = AsIs('footballapi_premierleague')
    data = get_train_data(params, league_avg_home_goals, league_avg_away_goals)

    data['elo_prob'] = data['home_elo'] - data['away_elo']
    data['elo_prob_home'] = data['elo_home'] - data['elo_away']
    data['elo_prob'] = data['elo_prob'].apply(probability_of_winning).round(2)
    data['elo_prob_home'] = data['elo_prob_home'].apply(probability_of_winning).round(2)

    data["homeodds"] = 1/ data['home_odds']

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

    model_logistic = classifier(
        x_train,
        y_train,
        features,
        None,
    )

    try:
        y_pred = model_logistic.predict_proba(df)
    except Exception as e:
        logging.error(f"Error in prediction for {home_name} vs {away_name}: {e}")
        return None

    # log probabilities
    prob_home = round(y_pred[0][0], 3)
    prob_away = round(y_pred[0][1], 3)
    prob_draw = round(y_pred[0][2], 3)

    odds_limit_home = round(1 / prob_home, 3)
    odds_limit_away = round(1 / prob_away, 3)
    odds_limit_draw = round(1 / prob_draw, 3)
    try:
        yield_home = round(odds_home * prob_home, 3)
        yield_away = round(odds_away * prob_away, 3)
        yield_draw = round(odds_draw * prob_draw, 3)
    except Exception as e:
        yield_home = None
        yield_away = None
        yield_draw = None
        pass

    title = f"Model for {home_name} vs {away_name}"
    table_str = tabulate(df, headers='keys', tablefmt='psql', showindex=True)
    # Prepend the title to the table string
    log_output = f"{title}\n{table_str}"
    # Log the table with the title
    logging.info("\n" + log_output)

    #logging.info(f"Odds: {round(1/odds_home, 2)}:{round(1/odds_draw, 2)}:{round(1/odds_away, 2)}")

    logging.info(
        f"Probabilities: {prob_home}, {prob_draw}, {prob_away} Odds: {odds_limit_home}/{odds_limit_draw}/{odds_limit_away}")
    logging.info(f"Odds: {odds_home} {odds_draw} {odds_away} Yield {yield_home} {yield_draw} {yield_away}")

    return {
        "prob_home": prob_home,
        "prob_draw": prob_draw,
        "prob_away": prob_away,
        "home_yield": yield_home,
        "draw_yield": yield_draw,
        "away_yield": yield_away,
    }