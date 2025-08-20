# RiverSense Server: Detailed Implementation Plan

This document outlines the complete, end-to-end plan for designing, building, and deploying the RiverSense server. The system is designed to ingest raw GNSS data from an Android application, process it to calculate a scientific data product (reflector height), and provide a robust interface for visualization and analysis.

---

## **Phase 1: Core Data Pipeline (The Engine)**

**Objective:** To create a robust, scalable, and automated pipeline that reliably ingests raw data, processes it, and stores the final, valuable result.

### **Step 1.1: Project Scaffolding & Environment Setup**
- [ ] Create the main project directory structure.
- [ ] Create the `docker-compose.yml` file defining the `api`, `worker`, `db`, `redis`, and `grafana` services.
- [ ] Create a `Dockerfile` for the `api` and `worker` services.
- [ ] In the Dockerfile, install Python and all necessary libraries (`fastapi`, `celery`, `sqlalchemy`, `psycopg2-binary`, `georinex`, `pandas`, `scipy`, `matplotlib`).
- [ ] In the Dockerfile, clone the `rokubun/android_rinex` repository.
- [ ] In the Dockerfile, copy the application code into the container.

### **Step 1.2: API Endpoint Implementation**
- [ ] In `api/main.py`, implement the `POST /upload` data ingestion endpoint using FastAPI.
- [ ] Define Pydantic models to validate the incoming JSON payload against the schema in `api.md`.
- [ ] Implement the endpoint logic to enqueue a task for the Celery worker and return a `200 OK` response.

### **Step 1.3: Data Conversion Logic**
- [ ] In `scripts/processing_pipeline.py`, create the primary function: `convert_json_to_rinex(json_data)`.
- [ ] Adapt the logic from `complete_rinex_converter.py` to accept a JSON object as input.
- [ ] Implement the programmatic formatting of JSON data into the intermediate text format.
- [ ] Implement the subprocess execution of the `gnsslogger_to_rnx` script.
- [ ] Ensure the function returns the file path to the newly generated RINEX `.obs` file.

### **Step 1.4: Background Worker Implementation**
- [ ] In `worker/tasks.py`, define the main Celery task: `process_gnss_data(json_data)`.
- [ ] Implement the call to `convert_json_to_rinex` to get the RINEX file.
- [ ] Implement the subprocess execution of `gfzrnx` to extract SNR data.
- [ ] Implement the Lomb-Scargle Periodogram analysis using `scipy`.
- [ ] Implement the reflector height calculation.
- [ ] Implement the statistical outlier rejection (e.g., Median Absolute Deviation).
- [ ] Implement the database logic to store the final, cleaned reflector height and associated metadata.

---

## **Phase 2: Data Utilization & Visualization (The Interface)**

**Objective:** To make the processed data accessible, understandable, and actionable for end-users.

### **Step 2.1: Data Serving API**
- [ ] In `api/main.py`, add new read-only endpoints.
- [ ] Implement `GET /api/v1/height/{station_id}` to serve time-series data.
- [ ] Implement `GET /api/v1/stations` to list all stations.
- [ ] Implement `GET /api/v1/station/{station_id}` for detailed station metadata.

### **Step 2.2: Dashboard and Visualization**
- [ ] Provision the Grafana service defined in `docker-compose.yml`.
- [ ] Create a configuration file to automatically provision Grafana with the PostgreSQL data source.
- [ ] Create a configuration file to automatically provision the "Primary Monitoring" dashboard.
- [ ] Build the time-series graph panel for reflector height.
- [ ] Build the Geomap panel for station locations.
- [ ] Build the Stat panels for key station metadata.

### **Step 2.3: Alerting**
- [ ] Within the Grafana dashboard configuration, define alerting rules.
- [ ] Create an alert for water level exceeding a critical threshold.
- [ ] Create an alert for a station failing to report new data.
- [ ] Create an alert for low device battery.

---

## **Phase 3: Advanced Features & Diagnostics**

**Objective:** To provide expert-level tools for data validation, troubleshooting, and manual quality control.

### **Step 3.1: Automated Diagnostic Visualizations**
- [ ] In `scripts/processing_pipeline.py`, create the function `generate_azimuth_mask(...)`.
- [ ] Implement the `matplotlib` logic to generate a polar plot (skyplot).
- [ ] Ensure the plot is saved as a PNG image.
- [ ] Update the worker to call this function and store the image path in the database.

### **Step 3.2: Deep-Dive Diagnostic Dashboard**
- [ ] Create a new "Diagnostics" dashboard in Grafana.
- [ ] Build an Image Panel to display the pre-generated azimuth mask image.
- [ ] Build an SNR plot panel to show raw SNR vs. sine(elevation) data.
- [ ] Build a Periodogram plot panel to show the Lomb-Scargle output.

### **Step 3.3: Manual Data Override (Optional Extension)**
- [ ] If required, implement a secure `POST /api/v1/height/override` endpoint.
- [ ] Implement the backend logic to update the database with a manually corrected value while preserving the original.
