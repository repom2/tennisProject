
-- Use the `ref` function to select from other models

select *
from {{ source('public', 'sportscore_leagues') }}
where id = '1000'
