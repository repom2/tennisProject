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
      ]
    ) }} as id,
    tour_id,
    winner_id,
    loser_id,
    date
from (
    select
        match_num,
        tourney_id as tour_id,
        case when b.id is null then winner_id else b.id end as winner_id,
        case when c.id is null then winner_id else c.id end as loser_id,
        to_date(tourney_date, 'YYYYMMDD') as date
    from tennis_atp_atpmatches a left join tennisapi_players b on winner_id = b.player_id::text
    left join tennisapi_players c on loser_id = c.player_id::text
    inner join tennisapi_atptour t on a.tourney_id=t.id where date <= '2023-02-27'

    union all

    select
        a.id as match_num,
        t.id as tour_id,
        case when winner_code = '1' then b.id else c.id end winner_id,
	    case when winner_code = '2' then b.id else c.id end loser_id,
        date(start_at) as date
    from sportscore_events a inner join tennisapi_atptour t
    on t.id=CONCAT(EXTRACT('Year' FROM date(start_at)), '-', a.league_id)
    left join tennisapi_players b on home_team_id::integer = b.sportscore_id
    left join tennisapi_players c on away_team_id::integer = c.sportscore_id
    where start_at::timestamp > '2023-02-27'
    and sport_id='2'
    and status = 'finished'
    and (winner_code = '1' or winner_code = '2')
) s
