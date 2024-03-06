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
    id::integer,
    tour_id,
    home_id::integer,
    away_id::integer,
    start_at::timestamp with time zone,
    round_name,
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
    event_id,
    winner_code,
    status,
	status_more,
	challenge_id::integer,
	home_odds::float,
	away_odds::float,
	home_score::integer,
	away_score::integer
from (
    select
        a.id,
        t.id as tour_id,
        home_team_id as home_id,
	    away_team_id as away_id,
        start_at,
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
        a.id as event_id,
        winner_code::integer,
        coalesce((replace(periods_time, '''', '"')::json ->> 'period_1_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_2_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_3_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_4_time')::integer, 0)
	    + coalesce((replace(periods_time, '''', '"')::json ->> 'period_5_time')::integer, 0) as court_time,
	    status,
	    status_more,
	    challenge_id::integer,
	    (main_odds ->> 'outcome_1')::json ->> 'value' as home_odds,
        (main_odds ->> 'outcome_2')::json ->> 'value' as away_odds,
        (home_score ->> 'current')::integer as home_score,
        (away_Score ->> 'current')::integer as away_score
    from sportscore_tennisevents a inner join tennis_api_atptour t
    on t.id::text=a.league_id
    inner join tennis_api_player b on home_team_id::integer = b.id
    inner join tennis_api_player c on away_team_id::integer = c.id
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
            sum(l_secondwon) as l_secondwon
        from (
        select
            stat_name,
            case when stat_name = 'firstin'
            then split_part(replace(home, '/', ' '), ' ', 1)::integer end as w_firstin,
            case when stat_name = 'firstin'
            then split_part(replace(home, '/', ' '), ' ', 2)::integer end as w_svpt,
            case when stat_name = 'aces'
            then home::integer end as w_aces,
            case when stat_name = 'df'
            then home::integer end as w_df,
            case when stat_name = 'svgms'
            then home::integer end as w_svgms,
            case when stat_name = 'bpfaced'
            then home::integer end as w_bpfaced,
            case when stat_name = 'bpsaved'
            then split_part(replace(home, '/', ' '), ' ', 1)::integer  end as w_bpsaved,
            case when stat_name = 'firstwon'
            then replace(replace(split_part(replace(home, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as w_firstwon,
            case when stat_name = 'secondwon'
            then replace(replace(split_part(replace(home, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as w_secondwon,
            case when stat_name = 'firstin'
            then split_part(replace(away, '/', ' '), ' ', 1)::integer end as l_firstin,
            case when stat_name = 'firstin'
            then split_part(replace(away, '/', ' '), ' ', 2)::integer end as l_svpt,
            case when stat_name = 'aces'
            then away::integer end as l_aces,
            case when stat_name = 'df'
            then away::integer end as l_df,
            case when stat_name = 'svgms'
            then away::integer end as l_svgms,
            case when stat_name = 'bpfaced'
            then away::integer end as l_bpfaced,
            case when stat_name = 'bpsaved'
            then split_part(replace(away, '/', ' '), ' ', 1)::integer end as l_bpsaved,
            case when stat_name = 'firstwon'
            then replace(replace(split_part(replace(away, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as l_firstwon,
            case when stat_name = 'secondwon'
            then replace(replace(split_part(replace(away, '/', ' '), ' ', 1), '%)', ''), '(', '')::integer end as l_secondwon,
            event
        from (
        select
            event_id as event,
            item_object ->> 'home' as home,
            item_object ->> 'away' as away,
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
                else 'other' end as stat_name,
                *
        from (
            select
                item_object ->> 'name' as name,
                item_object ->> 'period' as period,
                *
            from (
                select
                    item_object ->> 'event_id' as events_id,
                    *
                from
                    (
                        SELECT
                            arr.position,
                            arr.item_object
                        FROM sportscore_stats,
                            jsonb_array_elements((data ->> 'data')::jsonb) with ordinality arr(item_object, position)
                    ) s
                ) a inner join tennis_api_atpmatch b on b.id::text=a.events_id
            ) c where period = 'all'
        ) aa where stat_name != 'other'
        ) stats
        ) end_stats group by event
    ) s_stats on event=a.id::text
    where sport_id='2' and section_id='145' and status !='canceled'
) s
