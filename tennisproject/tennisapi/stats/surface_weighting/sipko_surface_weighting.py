import pandas as pd
from django.db import connection
import warnings
from psycopg2.extensions import AsIs
warnings.filterwarnings("ignore")


def standard_deviation(params):
    query = \
        """
        select
            surface,
            ROUND(STDDEV(win_percentage), 3) as  stddev,
            count(*) as number_of_players,
            ROUND(avg(win_percentage), 3) as mean_win_percentage
        from (
        select
        winner_id as player_id,
        s.surface,
        round(wins::numeric / (wins+loses) , 2) as win_percentage
        from 
        (select 
        winner_id,
        surface,
        count(*) as wins
        from %(matches_table)s a 
        where 
        a.date > %(date)s
        group by a.surface, winner_id) s
        inner join (
            select 
            loser_id,
            surface, 
            count(*) as loses
            from %(matches_table)s a
            where 
            a.date > %(date)s
            group by surface, loser_id
        ) l 
        on l.loser_id=s.winner_id and l.surface=s.surface
        ) std 
        where player_id in (
            select a.loser_id from (
        (select distinct loser_id from %(matches_table)s a
        where surface = %(surface_b)s and a.date > %(date)s) a inner join (select distinct loser_id from %(matches_table)s a
        where surface = %(surface_a)s and a.date > %(date)s) b on b.loser_id=a.loser_id
            )
        )
            and player_id in (
            select a.winner_id from (
        (select distinct winner_id from %(matches_table)s a
        where surface = %(surface_b)s and a.date > %(date)s) a inner join (select distinct winner_id from %(matches_table)s a
        where surface = %(surface_a)s and a.date > %(date)s) b on b.winner_id=a.winner_id) 
            )
        group by surface;
    """

    df = pd.read_sql(query, connection, params=params)
    print(df)

    return df


def surface_correlation(params):

    query = \
        """
        select sum(surface_a*surface_b) / (( %(number_of_players)s-1)* %(std_matches_won_surface_a)s *%(std_matches_won_surface_b)s) as correlation from (
            select player_id, sum(surface_a) as surface_a, sum(surface_b) as surface_b from (
            select
                player_id,
                case when surface = %(surface_a)s then (win_percentage) - 0.425
                else 0 end as surface_a,
                case when surface = %(surface_b)s then (win_percentage) - 0.444
                else 0 end as surface_b
            from (
            select
            winner_id as player_id,
            s.surface,
            round(wins::numeric / (wins+loses) , 2) as win_percentage
            from 
            (select 
            winner_id,
            surface,
            count(*) as wins
            from %(matches_table)s a 
            where 
            a.date > %(date)s
            group by a.surface, winner_id) s
            inner join (
                select 
                loser_id,
                surface, 
                count(*) as loses
                from %(matches_table)s a 
                where 
                a.date > %(date)s
                group by surface, loser_id
            ) l 
            on l.loser_id=s.winner_id and l.surface=s.surface
            ) std 
            where player_id in (
                select a.loser_id from (
            (select distinct loser_id from %(matches_table)s a
            where a.surface = %(surface_b)s and a.date > %(date)s) a inner join (select distinct loser_id from %(matches_table)s a
            where a.surface = %(surface_a)s and a.date > %(date)s) b on b.loser_id=a.loser_id
                )
            )
                and player_id in (
                select a.winner_id from (
            (select distinct winner_id from %(matches_table)s a
            where a.surface = %(surface_b)s and a.date > %(date)s) a inner join (select distinct winner_id from %(matches_table)s a
            where a.surface = %(surface_a)s and a.date > %(date)s) b on b.winner_id=a.winner_id) 
                ) and  (surface = %(surface_a)s or surface = %(surface_b)s)
            ) ss group by player_id
                ) sss;
    """

    df = pd.read_sql(query, connection, params=params)

    print(df)

    return df


def surface_weighting():
    surface_a = 'Clay'
    surface_b = 'Grass'
    params = {
        'surface_a': surface_a,
        'surface_b': surface_b,
        'tour_table': AsIs('tennisapi_wtatour'),
        'matches_table': AsIs('tennisapi_wtamatches'),
        'date': '1995-1-1',
        'std_matches_won_surface_a': None,
        'std_matches_won_surface_b': None,
        'number_of_players': None,
    }
    std = standard_deviation(params)

    surface_a_std = std[std['surface'] == surface_a]
    std_matches_won_surface_a = surface_a_std['stddev'].iloc[0]
    number_of_players_surface_a = surface_a_std['number_of_players'].iloc[0]

    surface_b_std = std[std['surface'] == surface_b]
    std_matches_won_surface_b = surface_b_std['stddev'].iloc[0]
    number_of_players_surface_b = surface_b_std['number_of_players'].iloc[0]

    print(std_matches_won_surface_a, number_of_players_surface_a)
    print(std_matches_won_surface_b, number_of_players_surface_b)

    params['std_matches_won_surface_a'] = std_matches_won_surface_a
    params['std_matches_won_surface_b'] = std_matches_won_surface_b
    if number_of_players_surface_a != number_of_players_surface_b:
        print("Number of players doesn't match on surfaces")
        return
    params['number_of_players'] = int(number_of_players_surface_b)

    corr = surface_correlation(params)
