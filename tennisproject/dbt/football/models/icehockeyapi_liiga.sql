{{
    config(
    indexes = [
        {'columns':['id'],'unique':True},
    ],
    unique_key = "id",
    full_refresh = false,
    on_schema_change='fail',
    tags = [ "top-level" ],
    )
}}

select
    e.id,
    slug,
    h.id as home_team_id,
    a.id as away_team_id,
    challenge_id::integer,
    status,
    status_more,
    TO_TIMESTAMP(
    start_at,
    'YYYY-MM-DD HH24:MI:SS'
    ) as start_at,
    home_team::json ->> 'name' as home_team_name,
    away_team::json ->> 'name' as away_team_name,
    (home_score::json ->> 'normal_time')::integer as home_score,
    (away_score::json ->> 'normal_time')::integer as away_score,
    ((main_odds::json ->> 'outcome_1')::json ->> 'value')::float as home_odds,
    ((main_odds::json ->> 'outcome_2')::json ->> 'value')::float as away_odds,
    ((main_odds::json ->> 'outcome_X')::json ->> 'value')::float as draw_odds,
    winner_code::integer,
    e.name
from sportscore_icehockeyevents e
inner join icehockeyapi_teams h on e.home_team_id=h.id
inner join icehockeyapi_teams a on e.away_team_id=a.id
where league_id = '7622'
