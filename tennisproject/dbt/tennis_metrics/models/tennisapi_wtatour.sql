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
	case when surface is not null then surface else (select ground_type from sportscore_tennisevents t
													 where t.league_id = idd limit 1) end as surface
from (
(select * from (select
	distinct tourney_id,
	EXTRACT('Year' FROM to_date(tourney_date, 'YYYYMMDD')) as year,
	to_date(tourney_date, 'YYYYMMDD') as tourney_date,
	tourney_name,
	surface,
	tourney_level
from tennis_atp_wtamatches) a left join (select * from (
	select
		id as idd,
		(select date(min(start_at)) from sportscore_tennisevents q where q.league_id=g.id) as start_date,
		name_translations ->> 'en' as tour_name,
		case when split_part(replace(slug, 'wta-', ''),'-',1) = 'open' then 'valencia'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'montreal' then 'canada'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'toronto' then 'canada'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'london' then 'queen'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'st' then 'petersburg'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 's' then 'hertogenbosch'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'nur' then 'astana'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'finals' then 'tour finals'
		when name_translations ->> 'en' ilike '%adelaide 2%' then 'adelaide 2'
		when name_translations ->> 'en' ilike '%adelaide' then 'adelaide 1'
		when name_translations ->> 'en' ilike '%belgrade 2%' then 'belgrade 2'
		when name_translations ->> 'en' ilike '%belgrade' then 'belgrade'
		when name_translations ->> 'en' ilike '%cologne II%' then 'cologne 2'
		when name_translations ->> 'en' ilike 'cologne  germany%' then 'cologne 1'
		else split_part(replace(slug, 'wta-', ''),'-',1) end as slug,
		case when start_date = '' then
		(select EXTRACT('Year' FROM date(min(start_at))) from sportscore_tennisevents q where q.league_id=g.id)
		else EXTRACT('Year' FROM date(start_date)) end as year,
		trim('"' FROM (section -> 'flag')::text) as section_slug
	from sportscore_tennistournaments g where slug not like '%doubles%' and name_translations ->> 'en' not ilike '%double%' ) sl where section_slug like '%wta%'
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
from tennis_atp_wtamatches) a right join (select * from (
	select
		id as idd,
		case when start_date = '' then
		(select date(min(start_at)) from sportscore_tennisevents q where q.league_id=gg.id)
		else date(start_date) end as start_date,
		name_translations ->> 'en' as tour_name,
		case when split_part(replace(slug, 'wta-', ''),'-',1) = 'open' then 'valencia'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'montreal' then 'canada'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'toronto' then 'canada'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'london' then 'queen'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'st' then 'petersburg'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 's' then 'hertogenbosch'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'nur' then 'astana'
		when split_part(replace(slug, 'wta-', ''),'-',1) = 'finals' then 'tour finals'
		when name_translations ->> 'en' ilike '%adelaide 2%' then 'adelaide 2'
		when name_translations ->> 'en' ilike '%adelaide' then 'adelaide 1'
		when name_translations ->> 'en' ilike '%belgrade 2%' then 'belgrade 2'
		when name_translations ->> 'en' ilike '%belgrade' then 'belgrade'
		when name_translations ->> 'en' ilike '%cologne II%' then 'cologne 2'
		when name_translations ->> 'en' ilike 'cologne  germany%' then 'cologne 1'
		else split_part(replace(slug, 'wta-', ''),'-',1) end as slug,
		case when start_date = '' then
		(select EXTRACT('Year' FROM date(min(start_at))) from sportscore_tennisevents q where q.league_id=gg.id)
		else EXTRACT('Year' FROM date(start_date)) end as year,
		trim('"' FROM (section -> 'flag')::text) as section_slug
	from sportscore_tennistournaments gg
	where slug not like '%doubles%' and name_translations ->> 'en' not ilike '%double%' ) sl
	where section_slug like '%wta%'
) b on tourney_name ilike '%' || slug || '%' and (start_date::timestamp - '11 day'::interval) < tourney_date
and (start_date::timestamp + '11 day'::interval) > tourney_date order by tourney_name
) ) a ) ss where date is not null

--insert into tennisapi_wtatour(id, name, date, surface)
--values('2023-10739', 'warsaw', '2023-7-24', 'Hard');
--values('2023-10987', 'WTA Ningbo, China Women Singles', '2023-9-24', 'Hard');
--2023-8866                                | WTA Cluj Napoca, Romania Women Singles        | 2023-10-14 | Clay --> Hard

--update tennisapi_wtatour set surface='Hard' where id='2023-6920'