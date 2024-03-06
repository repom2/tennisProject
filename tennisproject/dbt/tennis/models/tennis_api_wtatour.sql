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
    section_id::integer,
    slug,
    TO_TIMESTAMP(
    start_date,
    'YYYY-MM-DD HH24:MI:SS'
    ) as start_date,
    TO_TIMESTAMP(
    end_date,
    'YYYY-MM-DD HH24:MI:SS'
    ) as end_date,
    host::json ->> 'city' as city,
    host::json ->> 'country' as country,
    tennis_points::integer,
    ((
      SELECT value
      FROM jsonb_array_elements(facts) AS elements
      WHERE (elements ->> 'name') = 'Number of sets'
    )::json ->> 'value')::integer AS number_of_sets,
    (
      SELECT value
      FROM jsonb_array_elements(facts) AS elements
      WHERE (elements ->> 'name') ilike '%ground%type%'
    )::json ->> 'value' AS surface,
    (
      SELECT value
      FROM jsonb_array_elements(facts) AS elements
      WHERE (elements ->> 'name') = 'Prize currency'
    )::json ->> 'value' AS currency,
    ((
      SELECT value
      FROM jsonb_array_elements(facts) AS elements
      WHERE (elements ->> 'name') = 'Total prize money'
    )::json ->> 'value')::integer AS prize_money,
    (
      SELECT value
      FROM jsonb_array_elements(facts) AS elements
      WHERE (elements ->> 'name') = 'Continent'
    )::json ->> 'value' AS continent,
    ((
      SELECT value
      FROM jsonb_array_elements(facts) AS elements
      WHERE (elements ->> 'name') = 'Number of competitors'
    )::json ->> 'value')::integer AS number_of_competitors,
    most_count::integer
from sportscore_tennistournaments
where section_id = '144'