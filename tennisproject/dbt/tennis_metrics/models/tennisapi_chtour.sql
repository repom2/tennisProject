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

select * from (
select distinct
	CONCAT(EXTRACT('Year' FROM date(start_date)), '-', idd) as id,
	tour_name as name,
	date(start_date) as date,
	(select ground_type from sportscore_events t
    where t.league_id = idd limit 1) as surface
from (
	select
		id as idd,
		section ->> 'id' as section_id,
		case when start_date = '' then
		(select date(min(start_at)) from sportscore_events q where q.league_id=gg.id)
		else date(start_date) end as start_date,
		name_translations ->> 'en' as tour_name,
		slug,
		case when start_date = '' then
		(select EXTRACT('Year' FROM date(min(start_at))) from sportscore_events q where q.league_id=gg.id)
		else EXTRACT('Year' FROM date(start_date)) end as year,
		trim('"' FROM (section -> 'flag')::text) as section_slug
	from sportscore_leagues gg
	where slug not like '%doubles%' and name_translations ->> 'en' not ilike '%double%' ) sl
	where section_id = '143'
) b
