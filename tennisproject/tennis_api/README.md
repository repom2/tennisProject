### Using tennis_api    
docker compose exec tennisproject poetry run python manage.py sportscore tennis-tournaments
docker compose exec tennisproject poetry run python manage.py sportscore events-by-leagues
docker compose exec tennisproject poetry run python manage.py sportscore stats
docker compose exec tennisproject poetry run dbt run --project-dir dbt/tennis --profiles-dir dbt/tennis
docker compose exec tennisproject poetry run python manage.py elo wta 'hard'

docker compose exec tennisproject poetry run python manage.py prob pred 'at' 'indian'

