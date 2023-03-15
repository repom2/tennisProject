
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
    s.slug
from sportscore_leagues s
left join tennisapi_tournaments t on(t.id=s.id::numeric)

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
