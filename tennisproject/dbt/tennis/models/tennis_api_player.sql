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
    slug,
    name,
    name_short,
    name_full,
    gender,
    (details->> 'plays') as hand,
    (details->> 'weight') as weight,
    (details->> 'height_meters')::float as height,
    (details->> 'residence') as residence,
    (details->> 'birthplace') as birthplace,
    country_code,
    country,
    (details->> 'prize_total_euros')::integer as prize_total_euros,
    (details->> 'prize_current_euros')::integer as prize_current_euros,
    to_date(substring(details->> 'date_of_birth' from '\((.+)\)'), 'DD Mon YYY') dob
from  sportscore_teams a
where a.sport_id='2'


