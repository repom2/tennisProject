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
poetry run python manage.py sportscore events-by-leagues
dbt run --select tennisapi_atpmatches

### Elo Rating
poetry run python manage.py elo_rate atp 'hard'
