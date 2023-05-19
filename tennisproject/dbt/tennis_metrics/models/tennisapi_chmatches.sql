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
      'winner_id',
      'loser_id',
      'round_name',
      ]
    ) }} as id,
    tour_id,
    winner_id,
    loser_id,
    date,
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
    match_num::integer
from (
    select distinct
        a.id as match_num,
        t.id as tour_id,
        case when winner_code = '1' then b.id else c.id end winner_id,
	    case when winner_code = '2' then b.id else c.id end loser_id,
        date(start_at) as date,
        round_info ->> 'name' as round_name
    from sportscore_events a inner join tennisapi_chtour t
    on t.id=CONCAT(EXTRACT('Year' FROM date(start_at)), '-', a.league_id)
    left join tennisapi_players b on home_team_id::integer = b.sportscore_id
    left join tennisapi_players c on away_team_id::integer = c.sportscore_id
    and sport_id='2'
    and status = 'finished'
    and (winner_code = '1' or winner_code = '2')
) s
