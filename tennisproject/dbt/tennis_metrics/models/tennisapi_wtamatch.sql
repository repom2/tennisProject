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
    coalesce(time1, 0) + coalesce(time2, 0) + coalesce(time3, 0) as court_time
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
	    (replace(periods_time, '''', '"')::json ->> 'period_3_time')::integer as time3
    from (
        select *
            , case
            --when league_id = '8846' then '2042' --hamburg
            --when league_id = '10739' then '2037' --warsaw
            when league_id = '6979' then '1045' --washington
            when league_id = '6920' then '1082' --prague
            --when league_id = '7090' then '1094' --lausanne
            when league_id = '6925' then '2036' --budapest
            when league_id = '6965' then '466' --palermo
            else league_id
            end as league_idd
        from sportscore_events ) a inner join tennisapi_wtatour t
    on t.id=CONCAT(EXTRACT('Year' FROM date(start_at)), '-', a.league_idd)
    left join tennisapi_wtaplayers b on home_team_id::integer = b.sportscore_id
    left join tennisapi_wtaplayers c on away_team_id::integer = c.sportscore_id
    where start_at::timestamp > '2020-05-1'
    and sport_id='2'
    --and status = 'notstarted'
) s
