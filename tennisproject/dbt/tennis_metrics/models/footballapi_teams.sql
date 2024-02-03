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
from sportscore_teams where sport_id='1' and category_id='40'
