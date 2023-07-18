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
    away_odds,
    winner_code,
    coalesce(time1, 0)
    + coalesce(time2, 0)
    + coalesce(time3, 0)
    + coalesce(time4, 0)
    + coalesce(time5, 0) as court_time
from (
    select
        a.id as match_num,
        t.id as tour_id,
        b.id as home_id,
	    c.id as away_id,
        start_at,
        winner_code::integer,
        round_info ->> 'name' as round_name,
        (main_odds ->> 'outcome_1')::json ->> 'value' as home_odds,
        (main_odds ->> 'outcome_2')::json ->> 'value' as away_odds,
        (replace(periods_time, '''', '"')::json ->> 'period_1_time')::integer as time1,
	    (replace(periods_time, '''', '"')::json ->> 'period_2_time')::integer as time2,
	    (replace(periods_time, '''', '"')::json ->> 'period_3_time')::integer as time3,
	    (replace(periods_time, '''', '"')::json ->> 'period_4_time')::integer as time4,
	    (replace(periods_time, '''', '"')::json ->> 'period_5_time')::integer as time5
    from (
        select *
            --, case when league_id = '7168' then '0316'
            --when league_id = '7171' then '0314'
            --when league_id = '7200' then '0315'
            --else league_id
            --end as league_idd
        from sportscore_events ) a inner join tennisapi_atptour t
    on t.id=CONCAT(EXTRACT('Year' FROM date(start_at)), '-', a.league_id)
    left join tennisapi_players b on home_team_id::integer = b.sportscore_id
    left join tennisapi_players c on away_team_id::integer = c.sportscore_id
    where start_at::timestamp > '2022-05-1'
    and sport_id='2'
    --and status = 'notstarted'
) s
