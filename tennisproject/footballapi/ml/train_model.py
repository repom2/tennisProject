import warnings
import pandas as pd
from django.db import connection
import numpy as np
import logging
from tabulate import tabulate
from psycopg2.extensions import AsIs
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from tennisapi.ml.predict import probability_of_winning
from footballapi.stats.estimated_goals import estimated_goals
from footballapi.stats.poisson import calculate_poisson

# Configure logging
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore")


def get_train_data(params, league_avg_home_goals, league_avg_away_goals):
    """
    Fetch historical match data for training the prediction model.
    
    Args:
        params: Dictionary containing SQL query parameters
        league_avg_home_goals: Average home goals for the league
        league_avg_away_goals: Average away goals for the league
        
    Returns:
        DataFrame with match data and calculated features
    """
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
    
    # Calculate estimated goals using vectorized operations
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

    # Calculate Poisson probabilities
    df[['home_poisson', 'draw_poisson', 'away_poisson']] = pd.DataFrame(
        np.row_stack(
            np.vectorize(calculate_poisson, otypes=['O'])(
                df['home_est_goals'],
                df['away_est_goals'],
            )
        ), index=df.index)

    return df


def classifier(x_train, y_train, features):
    """
    Create and train a classifier model for match outcome prediction.
    
    Args:
        x_train: Training features
        y_train: Target values (match outcomes)
        features: List of feature names
        
    Returns:
        Trained model
    """
    # Create a logistic regression classifier for multi-class prediction
    classifier = LogisticRegression(
        multi_class='multinomial', 
        solver='lbfgs', 
        max_iter=1000
    )
    
    # Create a pipeline with the classifier
    pipeline = Pipeline([
        ('classifier', classifier)
    ])

    # Train the model
    model = pipeline.fit(x_train, y_train.values.ravel())
    
    # Store feature names in the model for later reference
    model.feature_names = features

    return model


def train_ml_model(row, level, params, league_avg_home_goals, league_avg_away_goals):
    """
    Train a model and make predictions for a specific match.
    
    Args:
        row: DataFrame row containing match data
        level: Competition level (e.g., 'premier', 'facup')
        params: SQL query parameters
        league_avg_home_goals: Average home goals for the league
        league_avg_away_goals: Average away goals for the league
        
    Returns:
        Dictionary with prediction probabilities and yield values
    """
    home_name = row['home_name']
    away_name = row['away_name']
    logger.info(f"Training model for {home_name} vs {away_name}")
    
    # Get odds data
    odds_home = row['home_odds']
    odds_away = row['away_odds']
    odds_draw = row['draw_odds']
    
    # Check if odds are available
    if odds_home is None or odds_away is None or odds_draw is None:
        logger.info(f"Odds are not available for {home_name} vs {away_name}")
        return None
    
    # Define features to use for prediction
    features = [
        'elo_prob',
        'home_poisson',
        'draw_poisson',
        'away_poisson',
    ]

    # Convert row to DataFrame for prediction
    match_data = row.to_frame().T
    df = match_data[features]

    # Special case for FA Cup
    if level == 'facup':
        params['match_table'] = AsIs('footballapi_premierleague')
    
    # Get training data
    data = get_train_data(params, league_avg_home_goals, league_avg_away_goals)

    # Calculate ELO-based probabilities
    data['elo_prob'] = data['home_elo'] - data['away_elo']
    data['elo_prob_home'] = data['elo_home'] - data['elo_away']
    data['elo_prob'] = data['elo_prob'].apply(probability_of_winning).round(2)
    data['elo_prob_home'] = data['elo_prob_home'].apply(probability_of_winning).round(2)

    # Select relevant columns
    columns_to_keep = features + ['winner_code', 'start_at', 'home_name', 'away_name']
    data = data[columns_to_keep]
    
    # Log data statistics
    data_length = len(data)
    data = data.dropna()
    logger.info(
        f"Data statistics: Total:{data_length}, "
        f"Home wins:{len(data[data['winner_code'] == 1])}, "
        f"Away wins:{len(data[data['winner_code'] == 2])}, "
        f"Draws:{len(data[data['winner_code'] == 3])}"
    )

    # Prepare training data
    x_train = data[features]
    y_train = data[['winner_code']]

    # Train the model
    model = classifier(x_train, y_train, features)

    # Make predictions
    try:
        y_pred = model.predict_proba(df)
    except Exception as e:
        logger.error(f"Error in prediction for {home_name} vs {away_name}: {e}")
        return None

    # Extract probabilities
    prob_home = round(y_pred[0][0], 3)
    prob_away = round(y_pred[0][1], 3)
    prob_draw = round(y_pred[0][2], 3)

    # Calculate fair odds
    odds_limit_home = round(1 / prob_home, 3)
    odds_limit_away = round(1 / prob_away, 3)
    odds_limit_draw = round(1 / prob_draw, 3)
    
    # Calculate yield values
    try:
        yield_home = round(odds_home * prob_home, 3)
        yield_away = round(odds_away * prob_away, 3)
        yield_draw = round(odds_draw * prob_draw, 3)
    except Exception:
        yield_home = None
        yield_away = None
        yield_draw = None

    # Log prediction details
    title = f"Model for {home_name} vs {away_name}"
    table_str = tabulate(df, headers='keys', tablefmt='psql', showindex=True)
    log_output = f"{title}\n{table_str}"
    logger.info("\n" + log_output)

    logger.info(
        f"Probabilities: {prob_home}, {prob_draw}, {prob_away} | "
        f"Fair odds: {odds_limit_home}/{odds_limit_draw}/{odds_limit_away}"
    )
    logger.info(
        f"Market odds: {odds_home}/{odds_draw}/{odds_away} | "
        f"Yield: {yield_home}/{yield_draw}/{yield_away}"
    )

    # Return prediction results
    return {
        "prob_home": prob_home,
        "prob_draw": prob_draw,
        "prob_away": prob_away,
        "home_yield": yield_home,
        "draw_yield": yield_draw,
        "away_yield": yield_away,
    }
