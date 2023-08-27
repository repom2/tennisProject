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
      'date'
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
    match_num::integer,
    court_time,
    w_ace,
    w_df,
    w_svpt,
    w_firstin,
    w_firstwon,
    w_secondwon,
    w_svgms,
    w_bpsaved,
    w_bpfaced,
    l_ace,
    l_df,
    l_svpt,
    l_firstin,
    l_firstwon,
    l_secondwon,
    l_svgms,
    l_bpsaved,
    l_bpfaced,
    event_id,
    winner_code
from (
    select distinct
        match_num,
        tourney_id as tour_id,
        case when b.id is null then winner_id else b.id end as winner_id,
        case when c.id is null then winner_id else c.id end as loser_id,
        to_date(tourney_date, 'YYYYMMDD') as date,
        round as round_name,
        minutes::integer * 60 as court_time,
        w_ace::integer,
        w_df::integer,
        w_svpt::integer,
        w_firstin::integer,
        w_firstwon::integer,
        w_secondwon::integer,
        w_svgms::integer,
        w_bpsaved::integer,
        w_bpfaced::integer,
        l_ace::integer,
        l_df::integer,
        l_svpt::integer,
        l_firstin::integer,
        l_firstwon::integer,
        l_secondwon::integer,
        l_svgms::integer,
        l_bpsaved::integer,
        l_bpfaced::integer,
        null as event_id,
        null as winner_code
    from tennis_atp_wtamatches a left join tennisapi_wtaplayers b on winner_id = b.player_id::text
    left join tennisapi_wtaplayers c on loser_id = c.player_id::text
    inner join tennisapi_wtatour t on a.tourney_id=t.id where date <= '2023-02-27'

    union all

    select
        a.id as match_num,
        t.id as tour_id,
        case when winner_code = '1' then b.id else c.id end winner_id,
	    case when winner_code = '2' then b.id else c.id end loser_id,
        date(start_at) as date,
        round_info ->> 'name' as round_name,
        null as court_time,
        null as w_ace,
        null as w_df,
        null as w_svpt,
        null as w_firstin,
        null as w_1stwon,
        null as w_2ndwon,
        null as w_svgms,
        null as w_bpsaved,
        null as w_bpfaced,
        null as l_ace,
        null as l_df,
        null as l_svpt,
        null as l_firstin,
        null as l_1stwon,
        null as l_2ndwon,
        null as l_svgms,
        null as l_bpsaved,
        null as l_bpfaced,
        a.id as event_id,
        winner_code
    from sportscore_events a inner join tennisapi_wtatour t
    on t.id=CONCAT(EXTRACT('Year' FROM date(start_at)), '-', a.league_id)
    left join tennisapi_wtaplayers b on home_team_id::integer = b.sportscore_id
    left join tennisapi_wtaplayers c on away_team_id::integer = c.sportscore_id
    where start_at::timestamp > '2023-02-27'
    and sport_id='2'
    and status = 'finished'
    and (winner_code = '1' or winner_code = '2')
) s
