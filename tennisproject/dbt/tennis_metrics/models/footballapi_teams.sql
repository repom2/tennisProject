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
    id,
    name,
    name_short
from sportscore_teams where sport_id='1'
and (
    category_id='40'
    or category_id='32' --spain
    or category_id='101' --italy
    or category_id='88' --germany
    or category_id='86' --france
    )
