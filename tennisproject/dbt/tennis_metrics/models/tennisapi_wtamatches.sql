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
    tourney_name,
    winner_name,
    loser_name,
    surface,
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
    winner_service_points_won::integer,
    winner_total_points::integer,
    winner_receiver_points_won::integer,
    loser_service_points_won::integer,
    loser_total_points::integer,
    loser_receiver_points_won::integer,
    event_id,
    winner_code
from (
    select distinct
        match_num,
        tourney_name,
        null as winner_name,
        null as loser_name,
        surface,
        tourney_id as tour_id,
        case when b.id is null then winner_id else b.id end as winner_id,
        case when c.id is null then winner_id else c.id end as loser_id,
        to_date(tourney_date, 'YYYYMMDD') as date,
        round as round_name,
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
        0 as winner_service_points_won,
        0 as winner_total_points,
        0 as winner_receiver_points_won,
        0 as loser_service_points_won,
        0 as loser_total_points,
        0 as loser_receiver_points_won,
        null as event_id,
        null as winner_code,
        minutes::integer * 60 as court_time
    from tennis_atp_wtamatches a
    inner join tennisapi_wtaplayers b on winner_id = b.player_id::text
    inner join tennisapi_wtaplayers c on loser_id = c.player_id::text

    union all

    select
        a.id as match_num,
        league ->> 'slug' as tourney_name,
        case when winner_code = '1' then home_team ->> 'name' else away_team ->> 'name' end as winner_name,
        case when winner_code = '2' then home_team ->> 'name' else away_team ->> 'name' end as loser_name,
        --(
          --SELECT value
          --FROM jsonb_array_elements(facts) AS elements
          --WHERE (elements ->> 'name') ilike '%ground%type%'
        --)::json ->> 'value' AS surface,
        ground_type as surface,
        league_id as tour_id,
        case when winner_code = '1' then b.id else c.id end winner_id,
	    case when winner_code = '2' then b.id else c.id end loser_id,
        date(start_at) as date,
        round_info ->> 'name' as round_name,
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
        CASE
            WHEN winner_service_points_won::text ~ '^[0-9]+$' THEN winner_service_points_won::integer
            ELSE NULL
        END as winner_service_points_won,
        CASE
            WHEN winner_total_points::text ~ '^[0-9]+$' THEN winner_total_points::integer
            ELSE NULL
        END as winner_total_points,
        CASE
            WHEN winner_receiver_points_won::text ~ '^[0-9]+$' THEN winner_receiver_points_won::integer
            ELSE NULL
        END as winner_receiver_points_won,
        CASE
            WHEN loser_service_points_won::text ~ '^[0-9]+$' THEN loser_service_points_won::integer
            ELSE NULL
        END as loser_service_points_won,
        CASE
            WHEN loser_total_points::text ~ '^[0-9]+$' THEN loser_total_points::integer
            ELSE NULL
        END as loser_total_points,
        CASE
            WHEN loser_receiver_points_won::text ~ '^[0-9]+$' THEN loser_receiver_points_won::integer
            ELSE NULL
        END as loser_receiver_points_won,
        a.id as event_id,
        winner_code,
        coalesce((replace(periods_time, '''', '"')::json ->> 'period_1_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_2_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_3_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_4_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_5_time')::integer, 0) as court_time
    from sportscore_tennisevents a
    left join sportscore_tennistournaments t on a.league_id = t.id
    left join tennisapi_wtaplayers b on home_team_id::integer = b.sportscore_id
    left join tennisapi_wtaplayers c on away_team_id::integer = c.sportscore_id
    left join (
        select
            event,
            sum(w_firstin) as w_firstin,
            sum(w_svpt) as w_svpt,
            sum(w_aces) as w_ace,
            sum(w_df) as w_df,
            sum(w_svgms) as w_svgms,
            sum(w_bpsaved) + sum(l_bpfaced) as w_bpfaced,
            sum(w_bpsaved) as w_bpsaved,
            sum(w_firstwon) as w_firstwon,
            sum(w_secondwon) as w_secondwon,
            sum(l_firstin) as l_firstin,
            sum(l_svpt) as l_svpt,
            sum(l_aces) as l_ace,
            sum(l_df) as l_df,
            sum(l_svgms) as l_svgms,
            sum(l_bpsaved) + sum(w_bpfaced) as l_bpfaced,
            sum(l_bpsaved) as l_bpsaved,
            sum(l_firstwon) as l_firstwon,
            sum(l_secondwon) as l_secondwon,
            sum(winner_service_points_won) as winner_service_points_won,
            sum(winner_total_points) as winner_total_points,
            sum(winner_receiver_points_won) as winner_receiver_points_won,
            sum(loser_service_points_won) as loser_service_points_won,
            sum(loser_total_points) as loser_total_points,
            sum(loser_receiver_points_won) as loser_receiver_points_won
        from (
        select
            stat_name,
            case when stat_name = 'service_points_won'
            then winner::integer end as winner_service_points_won,
            case when stat_name = 'total'
            then winner::integer end as winner_total_points,
            case when stat_name = 'receiver_points_won'
            then winner::integer end as winner_receiver_points_won,
            case when stat_name = 'service_points_won'
            then loser::integer end as loser_service_points_won,
            case when stat_name = 'total'
            then loser::integer end as loser_total_points,
            case when stat_name = 'receiver_points_won'
            then loser::integer end as loser_receiver_points_won,
            case when stat_name = 'firstin'
            then split_part(replace(winner, '/', ' '), ' ', 1)::integer end as w_firstin,
            case when stat_name = 'firstin'
            then split_part(replace(winner, '/', ' '), ' ', 2)::integer end as w_svpt,
            case when stat_name = 'aces'
            then winner::integer end as w_aces,
            case when stat_name = 'df'
            then winner::integer end as w_df,
            case when stat_name = 'svgms'
            then winner::integer end as w_svgms,
            case when stat_name = 'bpfaced'
            then winner::integer end as w_bpfaced,
            case when stat_name = 'bpsaved'
            then split_part(replace(winner, '/', ' '), ' ', 1)::integer  end as w_bpsaved,
            case when stat_name = 'firstwon'
            then replace(replace(split_part(replace(winner, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as w_firstwon,
            case when stat_name = 'secondwon'
            then replace(replace(split_part(replace(winner, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as w_secondwon,
            case when stat_name = 'firstin'
            then split_part(replace(loser, '/', ' '), ' ', 1)::integer end as l_firstin,
            case when stat_name = 'firstin'
            then split_part(replace(loser, '/', ' '), ' ', 2)::integer end as l_svpt,
            case when stat_name = 'aces'
            then loser::integer end as l_aces,
            case when stat_name = 'df'
            then loser::integer end as l_df,
            case when stat_name = 'svgms'
            then loser::integer end as l_svgms,
            case when stat_name = 'bpfaced'
            then loser::integer end as l_bpfaced,
            case when stat_name = 'bpsaved'
            then split_part(replace(loser, '/', ' '), ' ', 1)::integer end as l_bpsaved,
            case when stat_name = 'firstwon'
            then replace(replace(split_part(replace(loser, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as l_firstwon,
            case when stat_name = 'secondwon'
            then replace(replace(split_part(replace(loser, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as l_secondwon,
            event
        from (
        select
            event_id as event,
            case when winner_code = '2' then
            item_object ->> 'away'
            else item_object ->> 'home' end as winner,
            case when winner_code = '1' then
            item_object ->> 'away'
            else item_object ->> 'home' end as loser,
            *
        from (
        select
            case when name = 'first_serve' then 'firstin'
            when name = 'first_serve_points' then 'firstwon'
            when name = 'second_serve_points' then 'secondwon'
            when name = 'aces' then 'aces'
            when name = 'break_points_converted' then 'bpfaced'
            when name = 'break_points_saved' then 'bpsaved'
            when name = 'double_faults' then 'df'
            when name = 'service_games_played' then 'svgms'
            when name = 'service_points_won' then 'service_points_won'
            when name = 'total' then 'total'
            when name = 'receiver_points_won' then 'receiver_points_won'
            else 'other' end as stat_name,
            *
        from (
        select item_object ->> 'name' as name,
            item_object ->> 'period' as period, * from (
        select item_object ->> 'event_id' as events_id, * from (
        SELECT arr.position,arr.item_object
        FROM sportscore_stats,
        jsonb_array_elements((data ->> 'data')::jsonb) with ordinality arr(item_object, position)
        ) s ) a inner join tennisapi_wtamatches b on b.event_id=a.events_id
        ) c where period = 'all'
        ) aa where stat_name != 'other'
        ) stats
        ) end_stats group by event
    ) s_stats on event=a.id
    where start_at::timestamp > '2023-12-24'
    and a.sport_id='2'
    and (a.section ->> 'id'='144' or a.league ->> 'section_id'='144') and status !='canceled'
    and status = 'finished'
    and (winner_code = '1' or winner_code = '2')
) s
