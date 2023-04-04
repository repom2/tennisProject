
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

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
    s.id::integer,
    s.slug,
    s.section_id::integer,
    trim('"' FROM (section -> 'flag')::text) as section_slug,
    trim('"' FROM (section -> 'name')::text) as section_name,
    trim('"' FROM (section -> 'priority')::text) as priority,
    trim('"' FROM (name_translations -> 'en')::text) as name,
	facts.continent as continent,
	case when s.end_date = '' then null else s.end_date::timestamp with time zone end as end_date,
	facts.ground_type,
	facts.number_of_competitors::integer,
    facts.number_of_sets::integer,
	facts.prize_currency,
	case when s.start_date = '' then null else s.start_date::timestamp with time zone end as start_date,
	replace(facts.total_prize_money, ',', '')::integer as total_prize_money
from sportscore_leagues s
left join tennisapi_tournaments t on(t.id=s.id::integer)
left join (
select *
from crosstab(
	'select
		id,
		key,
		value
	from (
		select
		    s.id::numeric,
		    name as key,
		    value
		from (
		    SELECT
		        id,
		        slug,
		        x.*
		    FROM sportscore_leagues
		    ,json_to_recordset(facts::json) x
		    ( name text,
		    value text
		)
	) s ) as facts
	order by id asc, key asc',
	'select
		distinct key
		from (
		    select
		        s.id::numeric,
		        name as key,
		        value
		    from (
		    SELECT
		        id,
		        slug,
		        x.*
		    FROM sportscore_leagues
		    ,json_to_recordset(facts::json) x
		    ( name text,
		    value text
		    )
		    ) s order by id asc
		) as facts
		order by key asc'
) as ct(
    id text,
	"continent" text,
	"end_date" text,
	"ground_type" text,
	"number_of_competitors" text,
    "number_of_sets" text,
	"prize_currency" text,
	"start_date" text,
	"total_prize_money" text
    )
) facts on s.id = facts.id



