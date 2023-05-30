import warnings

import pandas as pd
from django.db import connection
import os

import joblib
import pandas as pd

warnings.filterwarnings("ignore")


def get_data():
    query = "select \
                date, \
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
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent " \
            "from ( \
            select \
                a.date, \
                home_odds, \
                away_odds, \
                h.last_name as winner_name, \
                aw.last_name as loser_name, \
                round_name, \
                (select elo from tennisapi_wtaelo el where el.player_id=home_id order by games desc limit 1) as winner_elo, \
                (select elo from tennisapi_wtahardelo el where el.player_id=home_id order by games desc limit 1) as winner_hardelo, \
                (select count(*) from tennisapi_wtaelo c where c.player_id=home_id and c.date < b.start_at) as winner_games, \
                (select count(*) from tennisapi_wtaelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.home_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select elo from tennisapi_wtaelo el where el.player_id=away_id order by games desc limit 1) as loser_elo,  \
                (select elo from tennisapi_wtahardelo el where el.player_id=away_id order by games desc limit 1) as loser_hardelo,  \
                (select count(*) from tennisapi_wtaelo c where c.player_id=away_id and c.date < b.start_at) as loser_games, \
                (select count(*) from tennisapi_wtaelo c inner join tennisapi_wtamatches aa on aa.id=c.match_id where c.player_id=b.away_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtaelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.away_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_wtaelo c \
                 inner join tennisapi_wtamatches aa on aa.id=c.match_id \
                 where c.player_id=b.home_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win \
            from tennisapi_wtatour a \
            inner join tennisapi_wtamatch b on b.tour_id=a.id \
            left join tennisapi_wtaplayers h on h.id = b.home_id \
            left join tennisapi_wtaplayers aw on aw.id = b.away_id \
            where name ilike '%garros%' and round_name not ilike 'qualification%' ) " \
            "ss where winner_name is not null and loser_name is not null;"

    df = pd.read_sql(query, connection)

    return df


def label_team(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data


def predict_matches_wta():
    data = get_data()
    print(data)
    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    file_name = "roland_garros_wta_model"
    file_path = local_path + file_name

    model = joblib.load(file_path)
    features = model.feature_names
    round_mapping = model.round_mapping

    data = label_team(data, round_mapping)
    print(features)

    data = data.dropna()
    x = data[features]
    print(x.head())

    y_pred = model.predict_proba(x)

    print(y_pred)

    data['y2'] = y_pred[:, 0]
    data['y1'] = y_pred[:, 1]
    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)
    print(data)
    data['yeald1'] = data['y1'] * data['home_odds']
    data['yeald2'] = data['y2'] * data['away_odds']

    print(data)
    data.to_csv('rg-wta.csv', index=False)

