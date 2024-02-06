### PREDICT
poetry run python manage.py football pred 'premier'

### ELO RATINGS
poetry run python manage.py football_elo championship-home

### UPDATE DATBASE
poetry run python manage.py sportscore football-events-by-leagues
dbt run --select footballapi_teams
dbt run --select footballapi_premierleague
dbt run --select footballapi_championship
dbt run --select footballapi_facup

