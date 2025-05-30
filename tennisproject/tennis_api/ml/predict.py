import warnings
import numpy as np
import pandas as pd
from django.db import connection
import os
from datetime import datetime, timedelta
from django.utils import timezone
import joblib
import logging
import sys
from tennis_api.stats.player_stats import player_stats
from tennis_api.stats.prob_by_serve.winning_match import matchProb
from tennis_api.stats.fatigue_modelling import fatigue_modelling
from tennis_api.stats.injury_modelling import injury_modelling
from tennis_api.stats.head2head import head2head
from psycopg2.extensions import AsIs
from tennis_api.stats.avg_swp_rpw_by_event import event_stats
from tennis_api.stats.common_opponent import common_opponent
from tennis_api.stats.analysis import match_analysis
from tennis_api.models import BetAtp, AtpMatch, Player, AtpTour, BetWta, WtaMatch, WtaTour
from tennis_api.ml.train_model import train_ml_model
import logging
from tabulate import tabulate

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


def probability_of_winning(x):
    l = (x) / 400
    prob2win = 1 / (1 + 10 ** (l))
    return 1 - prob2win


def get_data(params):
    query = \
        """
        select 
                match_id,
                home_id,
                away_id,
                start_at,
                winner_name,
                loser_name,
                home_odds,
                away_odds,
                round_name,
                case when (round_name ilike '%%ifinal%%' or round_name ilike '%%quarterfi%%') then 0
                    when (round_name ilike '%%r32%%' or round_name ilike '%%r16%%')  then 1 
                    when (round_name ilike '%%r64%%' or round_name ilike '%%r128%%')  then 2 
                else 3 end as round_code,
                winner_grasselo,
                winner_hardelo,
                winner_games,
                winner_year_games,
                winner_year_elo,
                winner_year_grass_games,
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent,
                case when winner_year_grass_games = 0 then 0 else round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) end as winner_win_grass_percent,
                loser_grasselo,
                loser_hardelo,
                loser_games,
                loser_year_games,
                loser_year_elo,
                loser_year_grass_games,
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent,
                case when loser_year_grass_games = 0 then 0 else round(loser_grass_win::numeric / loser_year_grass_games::numeric, 2) end as loser_win_grass_percent,
                case when winner_code = null then 10 else winner_code end,
                case when home_court_time is null then 0 else home_court_time / 60 end as home_court_time,
		        case when away_court_time is null then 0 else away_court_time / 60 end as away_court_time
            from (
            select 
                home_id,
                away_id,
                b.start_at,
                b.id as match_id,
                home_odds,
                away_odds,
                h.name_full as winner_name,
                aw.name_full as loser_name,
                round_name,
                winner_code,
                (select elo from %(grass_elo)s el where el.player_id=home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_grasselo,
                (select elo from %(hard_elo)s el where el.player_id=home_id and el.date < date(b.start_at) order by el.date desc limit 1) as winner_hardelo,
                (select count(*) from %(hard_elo)s c where c.player_id=home_id and c.date < date(b.start_at)) as winner_games,
                (select count(*) from %(hard_elo)s c inner join %(match_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as winner_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.home_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(match_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as winner_year_grass_games,
                (select elo from %(grass_elo)s el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_grasselo,
                (select elo from %(hard_elo)s el where el.player_id=away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,
                (select count(*) from %(hard_elo)s c where c.player_id=away_id and c.date < date(b.start_at)) as loser_games,
                (select count(*) from %(hard_elo)s c inner join %(match_table)s aa on aa.id=c.match_id where c.player_id=b.away_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as loser_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.away_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(match_table)s aa on aa.id=c.match_id where c.player_id=b.away_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as loser_year_grass_games,
                (select sum(case when aa.away_id=c.player_id then 1 else 0 end)
                 from %(hard_elo)s c
                 inner join %(match_table)s aa on aa.id=c.match_id
                 where c.player_id=b.away_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as loser_win,
                (select sum(case when aa.away_id=c.player_id then 1 else 0 end)
                 from %(grass_elo)s c
                 inner join %(match_table)s aa on aa.id=c.match_id
                 where c.player_id=b.away_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as loser_grass_win,
                 (select sum(case when aa.home_id=c.player_id then 1 else 0 end)
                 from %(hard_elo)s c
                 inner join %(match_table)s aa on aa.id=c.match_id
                 where c.player_id=b.home_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as winner_win,
            (select sum(case when aa.home_id=c.player_id then 1 else 0 end)
                 from %(grass_elo)s c
                 inner join %(match_table)s aa on aa.id=c.match_id
                 where c.player_id=b.home_id and aa.start_at < date(b.start_at) and EXTRACT(YEAR FROM aa.start_at)=EXTRACT(YEAR FROM b.start_at)) as winner_grass_win,
                (select sum(court_time) from %(match_table)s c
                where c.start_at between (b.start_at - interval '14 days') and c.start_at and
                c.start_at < b.start_at and (c.home_id=b.home_id or c.away_id=b.home_id)) as home_court_time,
                (select sum(court_time) from %(match_table)s c
                where c.start_at between (b.start_at - interval '14 days') and c.start_at and
                c.start_at < b.start_at and (c.home_id=b.away_id or c.away_id=b.away_id)) as away_court_time
            from %(tour_table)s a
            inner join %(match_table)s b on b.tour_id=a.id
            left join %(player_table)s h on h.id = b.home_id
            left join %(player_table)s aw on aw.id = b.away_id
            where surface ilike '%%%(surface)s%%' and b.start_at between %(start_at)s and %(end_at)s
            and (
            (a.slug ilike '%%%(tour)s%%' ))
            ) 
            ss where winner_name is not null and loser_name is not null order by start_at
    """

    df = pd.read_sql(query, connection, params=params)

    return df


def label_round(data, mapping):
    data['round_name'] = data['round_name'].map(mapping)
    return data


def predict(level, tour):
    surface = 'clay'
    now = timezone.now().date()
    end_at = now + timedelta(days=5)
    from_at = now - timedelta(days=1)

    if level == 'atp':
        qs = AtpMatch.objects.filter(
            tour__slug__icontains=tour,
            start_at__gte=from_at
        ).values_list('tour__surface', flat=True).first()
        logging.info('Surface: %s', qs)
        if 'Clay' in qs:
            surface = 'clay'
        logging.info('Surface: %s', surface)
        bet_qs = BetAtp.objects.all()
        match_qs = AtpMatch.objects.all()
        player_qs = Player.objects.all()
        tour_table = 'tennis_api_atptour'
        match_table = 'tennis_api_atpmatch'
        player_table = 'tennis_api_player'
        hard_elo = 'tennis_api_atpelohard'
        grass_elo = 'tennis_api_atpelograss'
        clay_elo = 'tennis_api_atpeloclay'
        if surface == 'clay':
            hard_elo = clay_elo
    else:
        bet_qs = BetWta.objects.all()
        match_qs = WtaMatch.objects.all()
        player_qs = Player.objects.all()
        tour_table = 'tennis_api_wtatour'
        match_table = 'tennis_api_wtamatch'
        player_table = 'tennis_api_player'
        hard_elo = 'tennis_api_wtaelohard'
        grass_elo = 'tennis_api_wtaelograss'
        clay_elo = 'tennis_api_wtaeloclay'
    params = {
        'tour_table': AsIs(tour_table),
        'match_table': AsIs(match_table),
        'player_table': AsIs(player_table),
        'match_table': AsIs(match_table),
        'hard_elo': AsIs(hard_elo),
        'grass_elo': AsIs(grass_elo),
        'clay_elo': AsIs(clay_elo),
        'tour': AsIs(tour),
        'start_at': now,
        'end_at': end_at,
        'surface': AsIs(surface),
    }
    data = get_data(params)

    l = len(data.index)
    if l == 0:
        print("No data")
        return

    columns = [
        'start_at',
        'winner_name',
        'loser_name',
        'home_id',
        'away_id',
    ]
    logging.info(
        f"DataFrame:\n{tabulate(data[columns], headers='keys', tablefmt='psql', showindex=True)}")

    if level == 'atp':
        tour_spw, tour_rpw = 0.645, 0.355
    else:
        tour_spw, tour_rpw = 0.565, 0.435

    date = '2015-1-1'
    params = {
        'event': AsIs(tour),
        'surface': AsIs(surface),
        'tour_table': AsIs(tour_table),
        'match_table': AsIs(match_table),
        'date': date,
    }
    event_spw, event_rpw = event_stats(params)

    if event_spw is None:
        if level == 'atp':
            event_spw, tour_spw, tour_rpw = 0.645, 0.645, 0.355
        else:
            event_spw, tour_spw, tour_rpw = 0.565, 0.565, 0.435
    print(event_spw)
    print(type(event_spw))
    data[['home_spw', 'home_rpw', 'home_matches']] = pd.DataFrame(
        np.row_stack(np.vectorize(player_stats, otypes=['O'])(data['home_id'], data['start_at'], params)),
        index=data.index)
    data[['away_spw', 'away_rpw', 'away_matches']] = pd.DataFrame(
        np.row_stack(np.vectorize(player_stats, otypes=['O'])(data['away_id'], data['start_at'], params)),
        index=data.index)
    data['player1'] = data.apply(lambda x: tour_spw + (x.home_spw - tour_spw) - (x.away_rpw - tour_rpw) if (x.away_rpw and x.home_spw) else None, axis=1)
    data['player2'] = data.apply(lambda x: tour_spw + (x.away_spw - tour_spw) - (x.home_rpw - tour_rpw) if (x.home_rpw and x.away_spw) else None, axis=1)
    # remove nan from player1 and player2
    data = data.dropna(subset=['player1', 'player2'])
    print(len(data))
    data['stats_win'] = data.apply(
        lambda x: matchProb(
            x.player1 if x.player1 else None,
            1-x.player2 if x.player2 else None,
            gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3
        ), axis=1).round(2)

    # Common opponent
    data[['spw1_c', 'spw2_c', 'common_opponents_count']] = pd.DataFrame(
        np.row_stack(np.vectorize(common_opponent, otypes=['O'])(
            params,
            data['home_id'],
            data['away_id'],
            event_spw,
            data['start_at']
        )
        ), index=data.index)

    data['common_opponents'] = data.apply(
        lambda x: matchProb(
            x.spw1_c,
            1 - x.spw2_c,
            gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3
        ), axis=1).round(2)

    data['home_fatigue'] = pd.DataFrame(
        np.row_stack(np.vectorize(fatigue_modelling, otypes=['O'])(
            data['home_id'],
            params['tour_table'],
            params['match_table'],
            params['start_at'],
            )
        ),
        index=data.index)
    data['away_fatigue'] = pd.DataFrame(
        np.row_stack(np.vectorize(fatigue_modelling, otypes=['O'])(
            data['away_id'],
            params['tour_table'],
            params['match_table'],
            params['start_at'],
        )
        ),
        index=data.index)
    data[['h2h_win', 'h2h_matches']] = pd.DataFrame(
        np.row_stack(np.vectorize(head2head, otypes=['O'])(
            data['home_id'],
            data['away_id'],
            params['tour_table'],
            params['match_table'],
            params['start_at'],
        )
        ),
        index=data.index)
    data['date'] = data['start_at'].dt.strftime('%Y-%m-%d')
    data[['walkover_home', 'home_inj_score']] = pd.DataFrame(
        np.row_stack(np.vectorize(injury_modelling, otypes=['O'])(
            data['date'],
            data['home_id'],
            params['tour_table'],
            params['match_table'],
        )
        ),
        index=data.index)
    data[['walkover_away', 'away_inj_score']] = pd.DataFrame(
        np.row_stack(np.vectorize(injury_modelling, otypes=['O'])(
            data['date'],
            data['away_id'],
            params['tour_table'],
            params['match_table'],
        )
        ),
        index=data.index)

    data['home_odds'] = data['home_odds'].astype(float)
    data['away_odds'] = data['away_odds'].astype(float)

    data['elo_prob'] = data['winner_hardelo'] - data['loser_hardelo']
    data['elo_prob'] = data['elo_prob'].apply(probability_of_winning).round(2)

    data['year_elo_prob'] = data['winner_year_elo'] - data['loser_year_elo']
    data['year_elo_prob'] = data['year_elo_prob'].apply(probability_of_winning).round(2)

    print('tour', tour_spw, tour_rpw)
    print('event', event_spw, event_rpw)
    #data = data.where(pd.notnull(data), None)
    data = data.replace(np.nan, None, regex=True)
    for index, row in data.iterrows():
        preview, reasoning = None, None#match_analysis(row)
        try:
            home_prob, away_prob, home_yield, away_yield = train_ml_model(row, level, params)
        except Exception as e:
            log.error(e)
            continue
        #break
        bet_qs.update_or_create(
            match=match_qs.filter(id=row.match_id)[0],
            home=player_qs.filter(id=row.home_id)[0],
            away=player_qs.filter(id=row.away_id)[0],
            defaults={
                "start_at": row.start_at,
                "home_name": row.winner_name,
                "away_name": row.loser_name,
                "home_odds": row['home_odds'],
                "away_odds": row['away_odds'],
                "elo_prob": row['elo_prob'],
                "year_elo_prob": row['year_elo_prob'],
                "home_spw": row['home_spw'],
                "home_rpw": row['home_rpw'],
                "away_spw": row['away_spw'],
                "away_rpw": row['away_rpw'],
                "home_stat_matches": row['home_matches'],
                "away_stat_matches": row['away_matches'],
                "stats_win": row['stats_win'],
                "home_fatigue": row['home_fatigue'],
                "away_fatigue": row['away_fatigue'],
                "h2h_win": row['h2h_win'],
                "h2h_matches": row['h2h_matches'],
                "walkover_home": row['walkover_home'],
                "walkover_away": row['walkover_away'],
                "home_inj_score": row['home_inj_score'],
                "away_inj_score": row['away_inj_score'],
                "common_opponents": row['common_opponents'],
                "common_opponents_count": row['common_opponents_count'],
                "preview": preview,
                "reasoning": reasoning,
                "home_prob": home_prob,
                "away_prob": away_prob,
                "home_yield": home_yield,
                "away_yield": away_yield,
            }
        )
