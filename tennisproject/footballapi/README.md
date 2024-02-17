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

poetry run python manage.py hockey pred 'liiga'

10 8 * * * docker compose exec tennisproject poetry run python manage.py sportscore football-events-by-leagues
11 8 * * * docker compose exec tennisproject poetry run python manage.py sportscore ice-hockey-events-by-leagues
12 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select footballapi_ligue1
13 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select footballapi_seriea
14 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select footballapi_laliga
15 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select footballapi_bundesliga
16 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select footballapi_premierleague
17 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select footballapi_championship
18 8 * * * docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis_metrics --profiles-dir dbt/tennis_metrics --select icehockeyapi_liiga
19 8 * * * docker compose exec tennisproject poetry run python manage.py hockey_elo liiga
20 8 * * * docker compose exec tennisproject poetry run python manage.py hockey_elo liiga-home
21 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo ligue1
22 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo ligue1-home
23 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo seriea
24 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo seriea-home
25 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo laliga
26 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo laliga-home
27 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo bundesliga
28 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo bundesliga-home
29 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo premier
30 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo premier-home
31 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo championship
32 8 * * * docker compose exec tennisproject poetry run python manage.py football_elo championship-home