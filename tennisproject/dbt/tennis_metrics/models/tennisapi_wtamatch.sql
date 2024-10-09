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
    tourney_name,
    home_name,
    away_name,
    surface,
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
    away_odds,
    home_score,
    away_score,
    winner_code,
    coalesce(time1, 0) + coalesce(time2, 0) + coalesce(time3, 0) as court_time
from (
    select
        a.id as match_num,
        league_id as tour_id,
        league ->> 'slug' as tourney_name,
        home_team ->> 'name' as home_name,
        away_team ->> 'name' as away_name,
        --(
          --SELECT value
          --FROM jsonb_array_elements(facts) AS elements
          --WHERE (elements ->> 'name') ilike '%ground%type%'
        --)::json ->> 'value' AS surface,
        ground_type as surface,
        b.id as home_id,
	    c.id as away_id,
        start_at,
        winner_code::integer,
        round_info ->> 'name' as round_name,
        (main_odds ->> 'outcome_1')::json ->> 'value' as home_odds,
        (main_odds ->> 'outcome_2')::json ->> 'value' as away_odds,
        (home_score ->> 'current')::integer as home_score,
        (away_Score ->> 'current')::integer as away_score,
        (replace(periods_time, '''', '"')::json ->> 'period_1_time')::integer as time1,
	    (replace(periods_time, '''', '"')::json ->> 'period_2_time')::integer as time2,
	    (replace(periods_time, '''', '"')::json ->> 'period_3_time')::integer as time3
    from sportscore_tennisevents a
    left join sportscore_tennistournaments t on a.league_id = t.id
    left join tennisapi_wtaplayers b on home_team_id::integer = b.sportscore_id
    left join tennisapi_wtaplayers c on away_team_id::integer = c.sportscore_id
    where
    a.sport_id='2' and (a.section ->> 'id'='144' or a.league ->> 'section_id'='144')
) s
