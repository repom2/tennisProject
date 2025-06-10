import pandas as pd
from django.db import connection


def get_data():
    query = (
        "select \
                date, \
                winner_name, \
                loser_name, \
                round_name, \
                winner_hard_elo + winner_change as winner_hard_elo, \
                winner_grass_elo, \
                winner_games, \
                winner_year_games, \
                winner_year_elo, \
                winner_year_grass_games, \
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent, \
                case when winner_year_grass_games = 0 then 0 else round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) end as winner_win_grass_percent, "
        "case when winner_court_time is null then 0 else winner_court_time / 60 end as winner_court_time, \
                loser_hard_elo - loser_change as loser_hard_elo, \
                loser_grass_elo, \
                loser_games, \
                loser_year_games, \
                loser_year_elo, \
                loser_year_grass_games, \
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent, "
        "case when loser_year_grass_games = 0 then 0 else round(loser_grass_win::numeric / loser_year_grass_games::numeric, 2) end as loser_win_grass_percent, "
        "case when loser_court_time is null then 0 else loser_court_time / 60 end as loser_court_time, "
        "1 as result "
        "from ( \
            select \
                a.date, \
                h.last_name as winner_name, \
                aw.last_name as loser_name, \
                round_name, \
                (select elo from tennisapi_atphardelo el where el.player_id=winner_id and el.date < b.date order by games desc limit 1) as winner_hard_elo, "
        "(select elo from tennisapi_atpgrasselo el where el.player_id=winner_id and el.date < b.date order by games desc limit 1) as winner_grass_elo, \
                (select elo_change from tennisapi_atphardelo el where el.player_id=winner_id and el.match_id=b.id) as winner_change, \
                (select count(*) from tennisapi_atphardelo c where c.player_id=winner_id and c.date < b.date) as winner_games, \
                (select count(*) from tennisapi_atphardelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.date < b.date and c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games, \
                (select sum(elo_change) from tennisapi_atphardelo c where c.date < b.date and c.player_id=b.winner_id and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM a.date)) as winner_year_elo, \
                (select count(*) from tennisapi_atpgrasselo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.date < b.date and c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_grass_games, \
                (select elo from tennisapi_atphardelo el where el.player_id=loser_id and el.date < b.date order by games desc limit 1) as loser_hard_elo, \
                (select elo from tennisapi_atpgrasselo el where el.player_id=loser_id and el.date < b.date order by games desc limit 1) as loser_grass_elo, \
                (select elo_change from tennisapi_atphardelo el where el.player_id=loser_id and el.match_id=b.id) as loser_change, \
                (select count(*) from tennisapi_atphardelo c where c.player_id=loser_id and c.date < b.date) as loser_games, \
                (select count(*) from tennisapi_atphardelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.date < b.date and c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games, \
                (select sum(elo_change) from tennisapi_atphardelo c where c.date < b.date and c.player_id=b.loser_id and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM a.date)) as loser_year_elo, \
                (select count(*) from tennisapi_atpgrasselo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.date < b.date and c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_grass_games, \
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atphardelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.date < b.date and c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                from tennisapi_atpgrasselo c \
                inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                where c.date < b.date and c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_grass_win, \
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atphardelo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.date < b.date and c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win, "
        "(select sum(case when aa.winner_id=c.player_id then 1 else 0 end) \
                 from tennisapi_atpgrasselo c \
                 inner join tennisapi_atpmatches aa on aa.id=c.match_id \
                 where c.date < b.date and c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_grass_win, "
        "(select sum(court_time) from tennisapi_atpmatches c "
        "where c.date between (b.date - interval '14 days') and b.date and "
        " (c.winner_id=b.winner_id or c.loser_id=b.winner_id)) as winner_court_time, "
        "(select sum(court_time) from tennisapi_atpmatches c "
        "where c.date between (b.date - interval '14 days') and b.date and "
        " (c.winner_id=b.loser_id or c.loser_id=b.loser_id)) as loser_court_time "
        "from tennisapi_atptour a \
            inner join tennisapi_atpmatches b on b.tour_id=a.id \
            left join tennisapi_players h on h.id = b.winner_id \
            left join tennisapi_players aw on aw.id = b.loser_id \
            where surface ilike '%hard%' "
        "and (name ilike '%canada%' "
        "or name ilike '%toronto%' "
        "or name ilike '%washing%' or name ilike '%winston%')and round_name not ilike 'qualification%' and "
        "a.date between '1995-1-1' and '2023-8-19' ) "
        "ss;"
    )

    df = pd.read_sql(query, connection)

    return df
