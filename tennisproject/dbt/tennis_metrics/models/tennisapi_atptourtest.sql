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
	case when tourney_id is not null then tourney_id else CONCAT(EXTRACT('Year' FROM date(start_date)), '-', idd) end as id,
	case when tourney_name is not null then tourney_name else tour_name end as name,
	case when tourney_date is not null then tourney_date else date(start_date) end as date,
	case when surface is not null then surface else (select ground_type from sportscore_events t
													 where t.league_id = idd limit 1) end as surface
from (
(select * from (select
	distinct tourney_id,
	EXTRACT('Year' FROM to_date(tourney_date, 'YYYYMMDD')) as year,
	to_date(tourney_date, 'YYYYMMDD') as tourney_date,
	tourney_name,
	surface,
	tourney_level
from tennis_atp_atpmatches) a left join (select * from (
	select
		id as idd,
		case when start_date = '' then
		(select date(min(start_at)) from sportscore_events q where q.league_id=g.id)
		else date(start_date) end as start_date,
		name_translations ->> 'en' as tour_name,
		case when split_part(replace(slug, 'atp-', ''),'-',1) = 'open' then 'valencia'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'montreal' then 'canada'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'toronto' then 'canada'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'london' then 'queen'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'st' then 'petersburg'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 's' then 'hertogenbosch'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'nur' then 'astana'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'finals' then 'tour finals'
		when name_translations ->> 'en' ilike '%adelaide 2%' then 'adelaide 2'
		when name_translations ->> 'en' ilike '%adelaide' then 'adelaide 1'
		when name_translations ->> 'en' ilike '%belgrade 2%' then 'belgrade 2'
		when name_translations ->> 'en' ilike '%belgrade' then 'belgrade'
		when name_translations ->> 'en' ilike '%cologne II%' then 'cologne 2'
		when name_translations ->> 'en' ilike 'cologne  germany%' then 'cologne 1'
		else split_part(replace(slug, 'atp-', ''),'-',1) end as slug,
		case when start_date = '' then
		(select EXTRACT('Year' FROM date(min(start_at))) from sportscore_events q where q.league_id=g.id)
		else EXTRACT('Year' FROM date(start_date)) end as year,
		trim('"' FROM (section -> 'flag')::text) as section_slug
	from sportscore_leagues g where slug not like '%doubles%' and name_translations ->> 'en' not ilike '%double%' ) sl where section_slug like '%atp%'
) b on tourney_name ilike '%' || slug || '%' and (start_date::timestamp - '11 day'::interval) < tourney_date
and (start_date::timestamp + '11 day'::interval) > tourney_date order by tourney_name
)
union all
(
select * from (select
	distinct tourney_id,
	EXTRACT('Year' FROM to_date(tourney_date, 'YYYYMMDD')) as year,
	to_date(tourney_date, 'YYYYMMDD') as tourney_date,
	tourney_name,
	surface,
	tourney_level
from tennis_atp_atpmatches) a right join (select * from (
	select
		id as idd,
		case when start_date = '' then
		(select date(min(start_at)) from sportscore_events q where q.league_id=gg.id)
		else date(start_date) end as start_date,
		name_translations ->> 'en' as tour_name,
		case when split_part(replace(slug, 'atp-', ''),'-',1) = 'open' then 'valencia'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'montreal' then 'canada'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'toronto' then 'canada'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'london' then 'queen'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'st' then 'petersburg'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 's' then 'hertogenbosch'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'nur' then 'astana'
		when split_part(replace(slug, 'atp-', ''),'-',1) = 'finals' then 'tour finals'
		when name_translations ->> 'en' ilike '%adelaide 2%' then 'adelaide 2'
		when name_translations ->> 'en' ilike '%adelaide' then 'adelaide 1'
		when name_translations ->> 'en' ilike '%belgrade 2%' then 'belgrade 2'
		when name_translations ->> 'en' ilike '%belgrade' then 'belgrade'
		when name_translations ->> 'en' ilike '%cologne II%' then 'cologne 2'
		when name_translations ->> 'en' ilike 'cologne  germany%' then 'cologne 1'
		else split_part(replace(slug, 'atp-', ''),'-',1) end as slug,
		case when start_date = '' then
		(select EXTRACT('Year' FROM date(min(start_at))) from sportscore_events q where q.league_id=gg.id)
		else EXTRACT('Year' FROM date(start_date)) end as year,
		trim('"' FROM (section -> 'flag')::text) as section_slug
	from sportscore_leagues gg where slug not like '%doubles%' and name_translations ->> 'en' not ilike '%double%' ) sl where section_slug like '%atp%'
) b on tourney_name ilike '%' || slug || '%' and (start_date::timestamp - '11 day'::interval) < tourney_date
and (start_date::timestamp + '11 day'::interval) > tourney_date order by tourney_name
) ) a ) ss where date is not null
