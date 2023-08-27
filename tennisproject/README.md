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
poetry run python manage.py sportscore stats
dbt run --select tennisapi_match
dbt run --select tennisapi_wtamatch
dbt run --select tennisapi_chmatch

### Elo Rating
poetry run python manage.py elo_rate atp 'hard'
poetry run python manage.py elo_rate wta 'grass'
poetry run python manage.py elo_rate wta 'grass'



#ATP
select 
	ss.*, 
	round(prob * home_odds, 2) as l1,
	round((1 - prob) * away_odds, 2) as l2
from (
select 
	start_at,
	home_p,
	away_p,
	home_odds::numeric,
	away_odds::numeric,
	home_elo,
	away_elo,
	home,
	away,
	round((1.0 / (1.0 + pow(10, ((away_elo - home_elo)::numeric / 400)))), 2) as prob
from (
select start_at, b.last_name as home_p, c.last_name as away_p, home_odds, away_odds, b.player_id, c.player_id,
(select elo from tennisapi_atpelo where b.id=player_id order by games desc limit 1) as home_elo,
(select elo from tennisapi_atpelo where c.id=player_id order by games desc limit 1) as away_elo,
(select count(*) from tennisapi_atpelo where b.id=player_id) as home,
(select count(*) from tennisapi_atpelo where c.id=player_id) as away
from tennisapi_match a
left join tennisapi_players b on home_id = b.id
left join tennisapi_players c on away_id = c.id
where start_at >= '2023-5-29' order by start_at::timestamp asc
) s where home_p is not null and away_p is not null) ss  ;

#WTA
select 
	ss.*, 
	round(prob * home_odds, 2) as l1,
	round((1 - prob) * away_odds, 2) as l2
from (
select 
	start_at,
	home_p,
	away_p,
	home_odds::numeric,
	away_odds::numeric,
	home_elo,
	away_elo,
	home,
	away,
	home_hardelo,
	away_hardelo,
	round((1.0 / (1.0 + pow(10, ((away_elo - home_elo)::numeric / 400)))), 2) as prob
from (
select start_at, b.last_name as home_p, c.last_name as away_p, home_odds, away_odds, b.player_id, c.player_id,
(select elo from tennisapi_wtaelo where b.id=player_id order by games desc limit 1) as home_elo,
(select elo from tennisapi_wtaelo where c.id=player_id order by games desc limit 1) as away_elo,
(select count(*) from tennisapi_wtaelo where b.id=player_id) as home,
(select count(*) from tennisapi_wtaelo where c.id=player_id) as away,
(select elo from tennisapi_wtahardelo where b.id=player_id order by games desc limit 1) as home_hardelo,
(select elo from tennisapi_wtahardelo where c.id=player_id order by games desc limit 1) as away_hardelo
from tennisapi_wtamatch a
left join tennisapi_wtaplayers b on home_id = b.id
left join tennisapi_wtaplayers c on away_id = c.id
where start_at >= '2023-5-29' order by start_at::timestamp asc
) s where home_p is not null and away_p is not null) ss  ;

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

### Best Elo
select 
	a.player_id, 
	first_name, 
	last_name, 
	max(date),
	(select elo from tennisapi_atpelo b where b.player_id=a.player_id order by games desc limit 1) as elo,
	(select count(*) from tennisapi_atpelo c where c.player_id=a.player_id) as games
from tennisapi_atpelo a
inner join tennisapi_atpmatches b on a.match_id=b.id
inner join tennisapi_players c on a.player_id=c.id
where date >= '2023-1-1'
group by a.player_id, first_name, last_name order by elo desc


### Machine learning query
select 
	date,
	winner_name,
	loser_name,
	round_name,
	winner_elo + winner_change as winner_elo,
	winner_games,
	winner_year_games,
	round(winner_win::numeric / winner_year_games::numeric, 2) as winner_win_percent,
	loser_elo - loser_change as loser_elo,
	loser_games,
	loser_year_games,
	round(loser_win::numeric / loser_year_games::numeric, 2) as loser_win_percent
from (
select 
	a.date,
	h.last_name as winner_name,
	aw.last_name as loser_name,
	round_name,
	(select elo from tennisapi_atpelo el where el.player_id=winner_id and el.match_id=b.id) as winner_elo,
	(select elo_change from tennisapi_atpelo el where el.player_id=winner_id and el.match_id=b.id) as winner_change,
	(select count(*) from tennisapi_atpelo c where c.player_id=winner_id and c.date < b.date) as winner_games,
	(select count(*) from tennisapi_atpelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_year_games,
	(select elo from tennisapi_atpelo el where el.player_id=loser_id and el.match_id=b.id) as loser_elo,
	(select elo_change from tennisapi_atpelo el where el.player_id=loser_id and el.match_id=b.id) as loser_change,
	(select count(*) from tennisapi_atpelo c where c.player_id=loser_id and c.date < b.date) as loser_games,
	(select count(*) from tennisapi_atpelo c inner join tennisapi_atpmatches aa on aa.id=c.match_id where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_year_games,
	(select sum(case when aa.winner_id=c.player_id then 1 else 0 end) 
	 from tennisapi_atpelo c 
	 inner join tennisapi_atpmatches aa on aa.id=c.match_id 
	 where c.player_id=b.loser_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as loser_win,
	 (select sum(case when aa.winner_id=c.player_id then 1 else 0 end) 
	 from tennisapi_atpelo c 
	 inner join tennisapi_atpmatches aa on aa.id=c.match_id 
	 where c.player_id=b.winner_id and EXTRACT(YEAR FROM aa.date)=EXTRACT(YEAR FROM a.date)) as winner_win
from tennisapi_atptour a
inner join tennisapi_atpmatches b on b.tour_id=a.id 
left join tennisapi_players h on h.id = b.winner_id
left join tennisapi_players aw on aw.id = b.loser_id
where name ilike '%garros%' and round_name not ilike 'qualification%' order by a.date desc
	) ss;