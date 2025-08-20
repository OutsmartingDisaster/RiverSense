# RiverSense Server

## Overview

The RiverSense server is a specialized solution for processing and analyzing GNSS (Global Navigation Satellite System) data using GNSS interferometric reflectometry (GNSS-IR). It handles data uploads from remote stations, processes raw GNSS data through a conversion pipeline, performs GNSS-IR analysis, and stores results in a database for further use.

The system is containerized using Docker and orchestrated with `docker-compose`, making it easy to set up and run in any environment.

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Building and Running the Application

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd riversense-server
    ```

2.  **Build and start the services:**

    ```bash
    docker-compose up --build
    ```

    This command will build the Docker images for the `api` and `worker` services and start all the services defined in the `docker-compose.yml` file.

3.  **Accessing the services:**

    Once the containers are running, you can access the different services at the following URLs:

    -   **API:** [http://localhost:8002](http://localhost:8002)
    -   **Grafana:** [http://localhost:3002](http://localhost:3002)

## Services

The `docker-compose` setup includes the following services:

- **`api`**: The main web server that provides a RESTful API for data submission.
    - **Purpose:** To receive GNSS data from remote stations
    - **Access Point:** `http://localhost:8002`

- **`worker`**: A Celery worker that performs asynchronous data processing tasks.
    - **Purpose:** To process raw GNSS data through:
        - RINEX format conversion
        - Quality control checks
        - GNSS-IR analysis
        - Water level calculations
    - **Access Point:** Internal only, processes tasks from Redis queue

- **`db`**: A PostgreSQL database for storing processed data.
    - **Purpose:** To persist raw and processed GNSS data
    - **Access Point:** `localhost:5400`

- **`redis`**: A Redis in-memory data store.
    - **Purpose:** Message broker for worker task queue
    - **Access Point:** Internal only

## API Authentication

The `/upload` endpoint is protected by bearer token authentication. To upload data, include an `Authorization` header with a valid bearer token.

### Example

```bash
curl -X POST "http://localhost:8002/upload" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_STATIC_TOKEN" \
-d '{
  "station_id": "station_A",
  "timestamp": "2025-08-17T12:00:00Z",
  "data": {
    "raw": "base64_encoded_raw_data",
    "nmea": ["$GPGGA,...", "$GPRMC,..."],
    "status": {
      "battery": 12.5,
      "temperature": 25.3,
      "humidity": 65
    }
  }
}'
```

The bearer token is read from the `BEARER_TOKEN` environment variable in the `api` service. You can set this variable in the `docker-compose.yml` file.

> **Note:** The default value for `BEARER_TOKEN` in the `docker-compose.yml` file is a placeholder and should be changed to a secure, randomly generated string in a production environment.

## Project Structure

```
riversense-server/
├── api/
│   └── main.py           # FastAPI application and endpoints
├── worker/
│   ├── tasks.py          # Celery task definitions
│   └── gnssir/           # GNSS-IR processing modules
│       ├── analysis.py   # GNSS-IR analysis functions
│       └── config.py     # Analysis configuration
├── scripts/
│   ├── processing_pipeline.py  # Data processing pipeline
│   ├── rinex_utils.py         # RINEX conversion utilities
│   └── gnssrefl_wrapper.py    # gnssrefl interface
├── database/
│   ├── models.py         # SQLAlchemy models
│   └── session.py        # Database session management
├── .gitignore           # Git ignore patterns
└── docker-compose.yml   # Service configuration
