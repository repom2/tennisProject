import pandas as pd
from django.db import connection


def get_data(params):
    query = """
        select

                match_id,
                home_id,
                away_id,
                home_player_id,
                away_player_id,
                start_at,
                home_fullname,
                away_fullname,
                case when atp_home_fullname is not null then atp_home_fullname
                else TRIM(split_part(home_fullname, ',', 2)) || ' ' || TRIM(split_part(home_fullname, ',', 1)) end as atp_home_fullname,
                case when atp_away_fullname is not null then atp_away_fullname
                when away_fullname is not null then TRIM(split_part(away_fullname, ',', 2)) || ' ' || TRIM(split_part(away_fullname, ',', 1)) end as atp_away_fullname,
                case when winner_first_name is not null then
                winner_first_name || ' ' || winner_name
                else winner_name end as winner_fullname,
                case when loser_first_name is not null then
                loser_first_name || ' ' || loser_name
                else loser_name end as loser_fullname,
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
                winner_grasselo_games,
                winner_hardelo,
                winner_hardelo_games,
                winner_clayelo,
                winner_clayelo_games,
                winner_games,
                winner_year_games,
                winner_year_elo,
                winner_year_grass_games,
                case when winner_year_games = 0 then 0 else round(winner_win::numeric / winner_year_games::numeric, 2) end as winner_win_percent,
                case when winner_year_grass_games = 0 then 0 else round(winner_grass_win::numeric / winner_year_grass_games::numeric, 2) end as winner_win_grass_percent,
                loser_grasselo,
                loser_grasselo_games,
                loser_hardelo,
                loser_hardelo_games,
                loser_clayelo,
                loser_clayelo_games,
                loser_games,
                loser_year_games,
                loser_year_elo,
                loser_year_grass_games,
                case when loser_year_games = 0 then 0 else round(loser_win::numeric / loser_year_games::numeric, 2) end as loser_win_percent,
                case when loser_year_grass_games = 0 then 0 else round(loser_grass_win::numeric / loser_year_grass_games::numeric, 2) end as loser_win_grass_percent,
                winner_code
            from (
            select
                b.home_id,
                b.away_id,
                b.start_at,
                b.id as match_id,
                h.name_full as home_fullname,
                aw.name_full as away_fullname,
                h.atp_name_full as atp_home_fullname,
                aw.atp_name_full as atp_away_fullname,
                h.player_id as home_player_id,
                aw.player_id as away_player_id,
                b.home_odds,
                b.away_odds,
                h.first_name as winner_first_name,
                aw.first_name as loser_first_name,
                h.last_name as winner_name,
                aw.last_name as loser_name,
                round_name,
                winner_code,
                (select elo from %(grass_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_grasselo,
                (select games from %(grass_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_grasselo_games,
                (select elo from %(clay_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_clayelo,
                (select games from %(clay_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_clayelo_games,
                (select elo from %(hard_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_hardelo,
                (select games from %(hard_elo)s el where el.player_id=b.home_id and el.date < date(b.start_at) order by games desc limit 1) as winner_hardelo_games,
                (select count(*) from %(hard_elo)s c where c.player_id=b.home_id and c.date < date(b.start_at)) as winner_games,
                (select count(*) from %(hard_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.home_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_year_grass_games,
                (select elo from %(grass_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_grasselo,
                (select games from %(grass_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_grasselo_games,
                (select elo from %(clay_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_clayelo,
                (select games from %(clay_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_clayelo_games,
                (select elo from %(hard_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo,
                (select games from %(hard_elo)s el where el.player_id=b.away_id and el.date < date(b.start_at) order by games desc limit 1) as loser_hardelo_games,
                (select count(*) from %(hard_elo)s c where c.player_id=b.away_id and c.date < date(b.start_at)) as loser_games,
                (select count(*) from %(hard_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_games,
                (select sum(elo_change) from %(hard_elo)s c where c.player_id=b.away_id and c.date < date(b.start_at) and EXTRACT(YEAR FROM c.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_elo,
                (select count(*) from %(grass_elo)s c inner join %(matches_table)s aa on aa.id=c.match_id where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_year_grass_games,
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(hard_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_win,
                (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(grass_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.away_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as loser_grass_win,
                 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(hard_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_win,
            (select sum(case when aa.winner_id=c.player_id then 1 else 0 end)
                 from %(grass_elo)s c
                 inner join %(matches_table)s aa on aa.id=c.match_id
                 where c.player_id=b.home_id and aa.date < date(b.start_at) and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM b.start_at)) as winner_grass_win
            from %(match_table)s b
            left join %(player_table)s h on h.id = b.home_id
            left join %(player_table)s aw on aw.id = b.away_id
            where
                b.surface ilike '%%%(query_surface)s%%' and
                b.start_at between %(start_at)s and %(end_at)s
            ) ss where winner_name is not null and loser_name is not null order by start_at
    """

    df = pd.read_sql(query, connection, params=params)

    return df
