### Reset the Development Environment

To reset the development environment and restart from a clean state, run

```bash
docker build tennisproject

docker compose down --volumes --rmi all


If you are using Docker Compose, Poetry can be used by prefixing commands with `docker compose exec app`. For example:

docker compose exec tennisproject bash

docker compose exec tennisproject poetry add <package name>

docker compose exec db psql -U tennis


### Available Scripts

In the project directory, you can run:

### Save leagues (tournaments) to sportscore tables
poetry run python manage.py sportscore leagues
poetry run python manage.py sportscore events

### DBT

crosstab function
CREATE EXTENSION IF NOT EXISTS tablefunc;
### Save data fro sportscore to tennisapi table

cd dbt/tennis_metrics

dbt run 

### UPDATE DATBASE
Work flow:
Get current League Ids
Get event data loop through League Ids
- Get Leagues
- Get Events

poetry run python manage.py sportscore leagues
dbt run --select tennisapi_atptour
poetry run python manage.py sportscore events-by-leagues
dbt run --select tennisapi_atpmatches
dbt run --select tennisapi_wtamatches
dbt run --select tennisapi_match
dbt run --select tennisapi_chmatch

### Elo Rating
poetry run python manage.py elo_rate atp 'clay'
poetry run python manage.py elo_rate wta 'clay'



#ATP
select * from (
select *,
	round((1.0 / (1.0 + pow(10, ((away_elo - home_elo)::numeric / 400)))), 2) as prob
from (
select start_at, b.last_name, c.last_name, home_odds, away_odds, b.player_id, c.player_id,
(select elo from tennisapi_atpelo where b.id=player_id order by games desc limit 1) as home_elo,
(select elo from tennisapi_atpelo where c.id=player_id order by games desc limit 1) as away_elo
from tennisapi_match a
left join tennisapi_players b on home_id = b.id
left join tennisapi_players c on away_id = c.id
where start_at >= '2023-5-22' order by start_at asc
) s ) ss where home_elo is not null and away_elo is not null;

#WTA
select * from (
select *,
	round((1.0 / (1.0 + pow(10, ((away_elo - home_elo)::numeric / 400)))), 2) as prob
from (
select start_at, b.last_name, c.last_name, home_odds, away_odds, b.player_id, c.player_id,
(select elo from tennisapi_wtaelo where b.id=player_id order by games desc limit 1) as home_elo,
(select elo from tennisapi_wtaelo where c.id=player_id order by games desc limit 1) as away_elo
from tennisapi_wtamatch a
left join tennisapi_wtaplayers b on home_id = b.id
left join tennisapi_wtaplayers c on away_id = c.id
where start_at >= '2023-5-22' order by start_at asc
) s ) ss where home_elo is not null and away_elo is not null;

### Players
select c.date,t.name, d.last_name as winner, e.last_name as loser from tennisapi_atpelo a 
inner join tennisapi_players b on b.id=a.player_id
inner join tennisapi_atpmatches c on c.id=a.match_id
inner join tennisapi_atptour t on t.id=c.tour_id
left join tennisapi_players d on d.id=c.winner_id
left join tennisapi_players e on e.id=c.loser_id
where b.last_name ilike '%Hurkacz%' order by c.date desc;

### Create backup
pg_dump -h db --clean tennis -U tennis > tennisproject.sql

docker compose cp tennisproject/app/tennisproject.sql .
