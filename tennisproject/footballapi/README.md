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


### ICE HOCKEY
poetry run python manage.py sportscore ice-hockey-events-by-leagues
dbt run --select icehockeyapi_teams
dbt run --select icehockeyapi_liiga
poetry run python manage.py hockey_elo liiga-home
