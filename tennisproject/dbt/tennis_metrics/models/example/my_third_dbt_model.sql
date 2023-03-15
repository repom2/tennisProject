{{
    config(
    materialized='table',
    schema = "public",
    on_schema_change='ignore'
    )
}}

with facts as (
            select
                s.id,
                replace(btrim(lower(name)), ' ', '_') as key,
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
         )

select *
from crosstab(
    'select
    id,
    key,
    value
    from (
            select
                s.id,
                replace(btrim(lower(name)), ' ', '_') as key,
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
         )
    group by id, key
    order by key',
    'select distinct key from facts order by key'
) as ct(
    id numeric,
    "number_of_sets" text,
    "ground_type" text,
	"number_of_competitors" text,
	"start_date" text,
	"end_date" text,
	"continent" text,
	"total_prize_money" text,
	"prize_currency" text
)
