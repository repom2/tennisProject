# SportScore API Data Fetcher

This project provides tools to fetch and manage sports data from the SportScore API, with a focus on football (soccer) and tennis data.

## Setup

1. Make sure you have the required dependencies installed:
   ```bash
   pip install django requests pandas tqdm tabulate
   ```
   
   Or if using Poetry:
   ```bash
   poetry add django requests pandas tqdm tabulate
   ```

2. Set your SportScore API key in your Django settings:
   ```python
   SPORT_SCORE_KEY = "your-api-key-here"
   ```

## Available Commands

The project is organized into separate modules for different sports:

### General Commands

```bash
# List all available sports
python manage.py sportscore sports
```

### Football Data Commands

```bash
# List all football sections (countries/regions)
python manage.py football_data sections

# List leagues in a specific section (e.g., England section ID is 40)
python manage.py football_data leagues-by-section

# Fetch events for major football leagues
python manage.py football_data events

# Fetch football teams
python manage.py football_data teams
```

### Tennis Data Commands

```bash
# List all tennis sections
python manage.py tennis_data sections

# Fetch tennis tournaments for ATP and WTA
python manage.py tennis_data tournaments

# Fetch tennis events by sections
python manage.py tennis_data events

# Fetch tennis players (in the API, tennis players are treated as teams)
python manage.py tennis_data players

# Fetch match statistics for tennis matches
python manage.py tennis_data stats
```

### Legacy Commands

The following commands are deprecated but still available through the main `sportscore` command:

```bash
# List sections for a specific sport
python manage.py sportscore sections

# List leagues by section ID
python manage.py sportscore leagues-by-section

# List all leagues
python manage.py sportscore leagues

# Fetch events by leagues
python manage.py sportscore events-by-leagues

# Fetch ice hockey events by leagues
python manage.py sportscore ice-hockey-events-by-leagues

# Fetch events by section ID
python manage.py sportscore events-by-section

# List all events
python manage.py sportscore events

# List all players
python manage.py sportscore players

# Fetch tennis players
python manage.py sportscore tennis-players

# List all teams
python manage.py sportscore teams

# Fetch match statistics
python manage.py sportscore stats
```

## API Structure

The SportScore API has a hierarchical structure:

1. **Sports** - Top level categories (football, tennis, etc.)
2. **Sections** - Countries or regions (England, Spain, ATP, WTA, etc.)
3. **Leagues/Tournaments** - Competitions within sections (Premier League, La Liga, etc.)
4. **Events** - Individual matches or games
5. **Teams/Players** - In tennis, players are represented as teams in the API

## Data Models

The project uses Django models to store the fetched data:

- `FootballEvents` - Football match data
- `TennisEvents` - Tennis match data
- `TennisTournaments` - Tennis tournament data
- `Teams` - Team data (including tennis players)
- `Players` - Player data
- `Stats` - Match statistics

## API Pagination Handling

The SportScore API uses pagination. Our fetchers handle this automatically by:

1. Making an initial request to get the first page
2. Checking the metadata for total pages/items
3. Making subsequent requests for additional pages
4. Combining all data before saving to the database

## Error Handling

The fetchers include error handling for common issues:
- JSON parsing errors
- Missing data in responses
- API rate limiting
- Network errors

## Notes on Tennis Data

In the SportScore API, tennis players are treated as teams. When fetching tennis player data, we use the teams endpoint with sport_id=2 (tennis).

## Workflow Example

A typical workflow for updating the database:

```bash
# 1. Fetch tennis tournaments
python manage.py tennis_data tournaments

# 2. Fetch tennis events
python manage.py tennis_data events

# 3. Fetch tennis players
python manage.py tennis_data players

# 4. Fetch match statistics
python manage.py tennis_data stats
```

## Docker Environment

If you are using Docker Compose, prefix commands with `docker compose exec`:

```bash
# Access the container shell
docker compose exec tennisproject bash

# Run commands inside the container
docker compose exec tennisproject python manage.py tennis_data events

# Add new dependencies
docker compose exec tennisproject poetry add <package name>

# Access the database
docker compose exec db psql -U tennis
```

## Reset Development Environment

To reset the development environment:

```bash
docker build tennisproject
docker compose down --volumes --rmi all
```

## DBT Integration

For data transformation with DBT:

```bash
# Install dependencies
poetry run dbt deps

# Run specific models
cd dbt/tennis_metrics/
dbt run --select tennisapi_atpmatches
dbt run --select tennisapi_wtamatches
dbt run --select tennisapi_match
dbt run --select tennisapi_wtamatch
```

## Elo Rating and Predictions

```bash
# Calculate Elo ratings for tennis
poetry run python manage.py elo_rate atp 'hard'
poetry run python manage.py elo_rate wta 'grass'

# Calculate Elo ratings for football teams in all leagues
poetry run python manage.py football_elo all

# Make predictions for tennis
poetry run python manage.py predict pred 'atp' 'austral'

# Make predictions for football leagues (e.g., Premier League)
poetry run python manage.py football pred 'premier'
```
