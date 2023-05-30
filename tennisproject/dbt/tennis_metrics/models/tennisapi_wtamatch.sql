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
    {{ dbt_utils.surrogate_key(
      [
      'match_num',
      'tour_id',
      'home_id',
      'away_id',
      ]
    ) }} as id,
    tour_id,
    home_id,
    away_id,
    start_at::timestamp with time zone,
    case when round_name = 'F' then 'Final'
    when round_name = 'Round of 128' then 'R128'
    when round_name = 'Round of 64' then 'R64'
    when round_name = 'Round of 32' then 'R32'
    when round_name = '1/32' then 'R32'
    when round_name = 'Round of 16' then 'R16'
    when round_name = '1/16' then 'R16'
    when round_name = 'SF' then 'Semifinal'
    when round_name = 'QF' then 'Quarterfinal'
    when round_name = '1/8' then 'Quarterfinal'
    else round_name end as round_name,
    match_num::integer,
    home_odds,
    away_odds
from (
    select
        a.id as match_num,
        t.id as tour_id,
        b.id as home_id,
	    c.id as away_id,
        start_at,
        round_info ->> 'name' as round_name,
        (main_odds ->> 'outcome_1')::json ->> 'value' as home_odds,
        (main_odds ->> 'outcome_2')::json ->> 'value' as away_odds
    from sportscore_events a inner join tennisapi_wtatour t
    on t.id=CONCAT(EXTRACT('Year' FROM date(start_at)), '-', a.league_id)
    left join tennisapi_wtaplayers b on home_team_id::integer = b.sportscore_id
    left join tennisapi_wtaplayers c on away_team_id::integer = c.sportscore_id
    where start_at::timestamp > '2023-05-27'
    and sport_id='2'
    and status = 'notstarted'
) s
