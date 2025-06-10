# Tennis Analytics Platform

A comprehensive sports analytics platform for tennis and football match predictions with machine learning models.

## Project Overview

This platform combines sports data analytics with machine learning to provide predictions and insights for tennis and football
matches. It's designed to analyze player statistics, calculate match probabilities, and provide betting recommendations based on
statistical models.

---

## Technologies Used

### Backend
- Python
- Django
- PostgreSQL
- Machine Learning (scikit-learn)
- RESTful APIs

### Frontend
- React.js
- TypeScript

### DevOps
- Docker
- Docker Compose

---

## Screenshots
![Screenshot 2025-05-12 160006](https://github.com/user-attachments/assets/282a1e7d-85d1-4de5-aa6a-1ade6815d7bd)
*Homepage: Instantly see latest match predictions and player statistics.*

![Screenshot 2025-05-12 at 15-50-34 Tennis AI](https://github.com/user-attachments/assets/1d839282-5ec6-4bda-8868-9fcc038ca58a)
*Match Calculator: Calculate match probabilities*

---

## Architecture

The application consists of:
- **Django Backend**: Handles data processing, ML model training, and API endpoints
- **React Frontend**: Provides user interface for viewing match predictions and statistics
- **PostgreSQL Database**: Stores player data, match results, and betting information
- **Docker**: Containerizes the application for consistent development and deployment

---

## Features

- Player statistics analysis
- ELO rating calculations
- Match outcome predictions
- Betting recommendations
- Head-to-head analysis
- Surface-specific performance metrics (clay, grass, hard court)
- Football match predictions

---

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Git

---

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/tennis-analytics-platform.git
    cd tennis-analytics-platform
    ```

2. **Create a `.env` file** with the required environment variables (see `.env.example`).

3. **Build and start the containers:**
    ```bash
    docker-compose up -d
    ```

4. **Access the application:**
    - **Frontend:** [http://localhost:3000](http://localhost:3000)
    - **Backend API:** [http://localhost:8000/tennisapi/](http://localhost:8000/tennisapi/)
    - **Admin interface:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

### API Documentation

The API is documented using the OpenAPI specification.  
You can view the API documentation at: [http://localhost:3000/api-docs](http://localhost:3000/api-docs)

---

### Machine Learning Models

The platform uses several ML models for predictions:
- Player performance prediction based on historical data
- Surface-specific performance models
- Head-to-head outcome predictions
- Fatigue modeling

---

### License

[MIT License](LICENSE)

