
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
    materialized='table',
    unique_key = "id",
    schema = "public",
    on_schema_change='ignore'
    )
}}

select
    s.id::numeric,
    s.slug,
	facts.continent,
	facts.end_date,
	facts.ground_type,
	facts.number_of_competitors,
    facts.number_of_sets,
	facts.prize_currency,
	facts.start_date,
	facts.total_prize_money
from sportscore_leagues s
left join tennisapi_tournaments t on(t.id=s.id::numeric)
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
		) s
		) as facts
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
		order by
	key asc'
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
)) facts on s.id = facts.id


