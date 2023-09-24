import warnings

import pandas as pd
from django.db import connection
import os

import joblib
from tennisapi.ml.player_stats import player_stats, player_stats_rpw
from tennisapi.stats.prob_by_serve.winning_match import matchProb

warnings.filterwarnings("ignore")


def probability_of_winning(x):
    l = (x) / 400
    prob2win = 1 / (1 + 10 ** (l))
    return 1 - prob2win


def get_data():
    query = "select \
                home_id, \
                away_id, \
                start_at, \
                winner_name, \
                loser_name, \
                home_odds, \
                away_odds, \
                round_name, \
                winner_grasselo, \
                winner_hardelo, \
                winner_games, \
                winner_year_games, \
                winner_year_elo, \
                winner_year_grass_games, \
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent, \
                case when winner_year_grass_games = 0 then 0 else round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) end as winner_win_grass_percent, \
                loser_grasselo, \
                loser_hardelo, \
                loser_games, \
                loser_year_games, \
                loser_year_elo, \
                loser_year_grass_games, \
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent, " \
                "case when loser_year_grass_games = 0 then 0 else round(loser_grass_win::numeric / loser_year_grass_games::numeric, 2) end as loser_win_grass_percent, " \
                "case when winner_code = null then 10 else winner_code end," \
                "case when home_court_time is null then 0 else home_court_time / 60 end as home_court_time, \
		        case when away_court_time is null then 0 else away_court_time / 60 end as away_court_time \
            from ( \
            select " \
                "home_id, \
                away_id, \
                b.start_at, \
                home_odds, \
                away_odds, \
                h.last_name as winner_name, \
                aw.last_name as loser_name, \
                round_name, \
                winner_code, \
                (select elo from tennisapi_atpgrasselo el where el.player_id=home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_grasselo, \
                (select elo from tennisapi_atphardelo el where el.player_id=home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_hardelo, \
                (select count(*) from tennisapi_atphardelo c where c.player_id=home_id and c.date < date(b.start_at)) as winner_games, \
                (select count(*) from tennisapi_atphardelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select sum(elo_change) from tennisapi_atphardelo c where c.player_id=b.home_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM a.date)) as winner_year_elo, \
                (select count(*) from tennisapi_atpgrasselo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_grass_games, \
                (select elo from tennisapi_atpgrasselo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_grasselo, " \
                "(select elo from tennisapi_atphardelo el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,  \
                (select count(*) from tennisapi_atphardelo c where c.player_id=away_id and c.date < date(b.start_at)) as loser_games, \
                (select count(*) from tennisapi_atphardelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select sum(elo_change) from tennisapi_atphardelo c where c.player_id=b.away_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM a.date)) as loser_year_elo, \
                (select count(*) from tennisapi_atpgrasselo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_grass_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atphardelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, " \
                "(select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpgrasselo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_grass_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atphardelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win, " \
            "(select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpgrasselo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_grass_win," \
                "(select sum(court_time) from tennisapi_match c " \
                "where c.start_at between (b.start_at - interval '14 days') and c.start_at and " \
                "c.start_at < b.start_at and (c.home_id=b.home_id or c.away_id=b.home_id)) as home_court_time, " \
                "(select sum(court_time) from tennisapi_match c " \
                "where c.start_at between (b.start_at - interval '14 days') and c.start_at and " \
                "c.start_at < b.start_at and (c.home_id=b.away_id or c.away_id=b.away_id)) as away_court_time  \
            from tennisapi_atptour a \
            inner join tennisapi_match b on b.tour_id=a.id \
            left join tennisapi_players h on h.id = b.home_id \
            left join tennisapi_players aw on aw.id = b.away_id \
            where surface ilike '%hard%' " \
            "and ( " \
            " " \
            "(name ilike '%chen%' ))" \
            "and round_name not ilike 'qualification%' ) " \
            "ss where winner_name is not null and loser_name is not null order by start_at;"

    df = pd.read_sql(query, connection)

    return df


def label_round(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data


def atlanta_pred():
    data = get_data()

    l = len(data.index)
    print(l)
    if l == 0:
        return

    local_path = os.getcwd() + '/tennisapi/ml/trained_models/'

    #file_name = "atlanta"
    file_name = "atlanta_rf"

    file_name = "toronto_gra" # only canada tournament
    file_name = "toronto_rf" # only canada tournament
    file_name = "cinci_gra"
    #file_name = "cinci_rf"
    file_name = "cinci_lin2"
    file_name = "winston_lin2"
    file_name = "usopen_lin"
    file_name = "usopen_lin2"
    file_name = "usopen_log"

    file_path = local_path + file_name

    model = joblib.load(file_path)
    features = model.feature_names
    round_mapping = model.round_mapping

    data = label_round(data, round_mapping)

    #print(data.loc[[238]].T)
    #data.at[250, 'home_odds'] = 1.2
    #data.at[3, 'home_odds'] = 4.0
    #data.at[250, 'away_odds'] = 5
    #data.at[3, 'away_odds'] = 1.25
    data['dr1'] = data['home_id'].apply(player_stats).round(2)
    data['rpw1'] = data['home_id'].apply(player_stats_rpw).round(2)
    data['dr2'] = data['away_id'].apply(player_stats).round(2)
    data['rpw2'] = data['away_id'].apply(player_stats_rpw).round(2)
    data['win'] = data.apply(lambda x: matchProb(x.dr1, 1-x.dr2, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=5), axis=1).round(
        2)

    #data = data.dropna()
    """x = data[features]
    l = len(x)
    print(l)
    #print(data.head())
    try:
        y_pred = model.predict_proba(x)
        data['y2'] = y_pred[:, 0]
        data['y1'] = y_pred[:, 1]
    except:
        # Lin
        y_pred = model.predict(x)
        data['y1'] = y_pred
        data['y2'] = 1 - data['y1']

    data['y2'] = data['y2'].round(2)
    data['y1'] = data['y1'].round(2)
    data['yield1'] = (data['y1'] * data['home_odds']).round(2)
    # data['yield1'] = (data['win'] * data['home_odds']).round(2)
    data['yield1'] = (data['prob'] * data['home_odds']).round(2)
    data['yield2'] = ((1 - data['prob']) * data['home_odds']).round(2)"""

    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)
    #data['winner_code'] = data['winner_code'].astype(int)
    #data['winner_grasselo'] = data['winner_grasselo'].astype(int)
    #data['loser_grasselo'] = data['loser_grasselo'].astype(int)

    data['prob'] = data['winner_hardelo'] - data['loser_hardelo']
    data['prob'] = data['prob'].apply(probability_of_winning).round(2)

    data['prob_year'] = data['winner_year_elo'] - data['loser_year_elo']
    data['prob_year'] = data['prob_year'].apply(probability_of_winning).round(2)

    #data['yield2'] = (data['y2'] * data['away_odds']).round(2)
    #data['yield2'] = ((1 - data['win']) * data['away_odds']).round(2)
    #data['yield2'] = ((1 - data['prob']) * data['away_odds']).round(2)

    data["bankroll"] = None
    data["bankroll2"] = None
    bankroll = 1000
    bankroll2 = 1000
    max_bet = 0.1
    for index, row in data.iterrows():
        continue
        try:
            yield1 = row["yield1"] - 0.0
            yield2 = row["yield2"] - 0.0
        except:
            continue

        if yield1 > 1.0:# and row.home_odds < 4 and row.home_odds > 1:
            bet2 = ((yield1 - 1) / (row.home_odds - 1)) * bankroll2
            limit = bankroll2 * max_bet
            if bet2 > limit:
                bet2 = limit
            if row.winner_code == 2:
                bankroll -= 100
                bankroll2 -= bet2
            elif row.winner_code == 1:
                bankroll += (100 * (row.home_odds - 1))
                bankroll2 += (bet2 * (row.home_odds - 1))
            else:
                continue
        elif yield2 > 1.0:# and row.away_odds < 4 and row.away_odds > 1:
            try:
                bet2 = ((yield2 - 1) / (row.away_odds - 1)) * bankroll2
            except:
                bet2 = 0.05*bankroll2
            limit = bankroll2 * max_bet
            if bet2 > limit:
                bet2 = limit
            if row.winner_code == 1:
                bankroll -= 100
                bankroll2 -= bet2
            elif row.winner_code == 2:
                bankroll += (100 * (row.away_odds - 1))
                bankroll2 += (bet2 * (row.away_odds - 1))
            else:
                continue
        else:
            continue
        data.loc[index, 'bankroll'] = round(bankroll, 0)
        data.loc[index, 'bankroll2'] = round(bankroll2, 0)

    columns = [
        'start_at',
        'winner_name',
        'loser_name',
        'home_odds',
        'away_odds',
        #'home_court_time',
        #'away_court_time',
        #'winner_grasselo',
        #'winner_games',
        #'winner_year_games',
        #'winner_win_percent',
        'prob',
        'prob_year',
        #'loser_grasselo',
        #'loser_games',
        #'loser_year_games',
        #'loser_win_percent',
        #'winner_code',
        #'y1',
        #'y2',
        #'yield1',
        #'yield2',
        #'bankroll',
        #'bankroll2',
        'dr1',
        'rpw1',
        'dr2',
        'rpw2',
        'win',

    ]

    print(data[columns])
    data.to_csv('grass-atp.csv', index=False)
    player_stats('df')
