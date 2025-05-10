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
poetry run dbt deps

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
cd dbt/tennis_metrics/
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

poetry run python manage.py predict pred 'atp' 'austral'