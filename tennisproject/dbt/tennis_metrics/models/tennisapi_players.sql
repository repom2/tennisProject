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
      ['sportscore_id',
      'player_id']
  ) }} as id,
    s.*
from (
select
    id::integer as sportscore_id,
    player_id::integer,
    a.dob,
    hand,
    ioc as country_code,
    case when height = 'nan' then null else height::float end,
    wikidata_id,
    name_last as last_name,
    name_first as first_name,
    lower(CONCAT(name_first, '-', name_last)) as slug
from
    (select
        to_date(dob, 'YYYYMMDD') dob,
        ioc,
        name_last,
        name_first,
        player_id,
        hand,
        height,
        wikidata_id
    from tennis_atp_players where dob != 'nan') a
left join
    (select
        id, slug, country_code, to_date(substring(details->> 'date_of_birth'
    from '\((.+)\)'), 'DD Mon YYY') dob
    from  sportscore_teams
    where sport_id='2') b on a.dob=b.dob and country_code=ioc and slug ilike '%' || name_last || '%'
) s ) z left join tennisapi_players p on (z.id=p.id)
