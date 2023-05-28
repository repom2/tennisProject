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
select z.* from (
select
    {{ dbt_utils.surrogate_key(
      [
      'sportscore_id',
      'player_id',
      'last_name'
      ]
  ) }} as id,
    s.*
from (
select
    id::integer as sportscore_id,
    player_id::integer,
    case when a.dob is null then b.dob else a.dob end as dob,
    hand,
    case when ioc is null then country_code else ioc end as country_code,
    case when height = 'nan' then null else height::float end,
    wikidata_id,
    case when name_last is null then name_full else name_last end as last_name,
    name_first as first_name,
    lower(CONCAT(name_first, '-', name_last)) as slug,
    country,
    prize_total_euros::integer as prize_total_euros
from
    (select
        case when dob != 'nan' then to_date(dob, 'YYYYMMDD') else null end as dob,
        ioc,
        name_last,
        name_first,
        player_id,
        hand,
        height,
        wikidata_id
    from tennis_atp_wtaplayers) a
full join
    (select distinct
        a.id,
        a.slug,
        country_code,
        country,
        details->> 'prize_total_euros' as prize_total_euros,
        name_full,
        to_date(substring(details->> 'date_of_birth'
    from '\((.+)\)'), 'DD Mon YYY') dob
    from  sportscore_teams a
    inner join sportscore_events b on (home_team_id=a.id or away_team_id=a.id)
    where a.sport_id='2' and section ->> 'id' = '144' and name_full not like '%/%' and a.slug !~ '[0-9]+') b
    on a.dob=b.dob and
    (slug ilike '%' || replace(name_last, ' ', '%') || '%'
    or slug ilike '%' || replace(name_first, ' ', '%') || '%')
) s ) z

