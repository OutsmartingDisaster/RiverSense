# RiverSense Server Documentation

This document outlines the architecture and setup for the RiverSense server, which is responsible for receiving, processing, and storing GNSS data from the Android app.

## 1. Overview

The server is designed to handle periodic uploads of compressed GNSS data from multiple stations. It provides a simple and robust API for data submission and includes a processing pipeline to make the data useful for analysis.

### 1.1. Architectural Approach: Client-Server Model

It is critical to understand that the Android app (the client) should **not** connect directly to the database (e.g., PostgreSQL). Instead, the app communicates with a web server API, which then securely interacts with the database. This is a standard, secure architectural pattern that provides several key benefits:

-   **Security:** A direct database connection would require embedding the database password in the app's code, making it vulnerable to extraction. A web server acts as a secure gatekeeper, preventing direct access to the database.
-   **Stability and Control:** The web server can validate all incoming data, manage connections from many devices, and handle network errors gracefully, protecting the database from corruption and overload.
-   **Scalability and Maintenance:** If the database credentials or location change, only the server configuration needs to be updated. The app does not need to be redeployed to all users.

The architecture outlined in this document follows this secure model, ensuring that data is transferred automatically and securely from the app to the database via the web server.

## 2. Data Transmission Strategy

The data transmission strategy is a **periodic, automated background upload**. The Android app will:

-   Collect GNSS data and store it locally.
-   Batch the collected data into a JSON object every 5 minutes.
-   Upload the JSON payload to the server automatically in the background.
-   Prioritize using mobile data for uploads to ensure timely data transmission.
-   Implement a retry mechanism for failed uploads to ensure data reliability.

## 3. Server Setup

The server can be built using a variety of technologies. For this documentation, we will provide a generic setup that can be adapted to your preferred stack (e.g., Python with Flask/Django, Node.js with Express, etc.).

### 3.1. Prerequisites

-   A server.
-   A Postgresql database for storing the processed data.
-   A programming language and web framework of your choice.

### 3.2. API Endpoint

The server will expose a single API endpoint for data submission:

-   **Endpoint:** `/upload`
-   **Method:** `POST`
-   **Content-Type:** `application/json`

The request body will be a JSON object containing the batched GNSS data. See the `api.md` file for a detailed schema.

### 3.3. Data Processing Pipeline

Upon receiving a data upload, the server will perform the following steps:

1.  **Authentication (Optional but Recommended):** Verify the request is from a trusted source using an API key or other authentication mechanism.
2.  **Validation:** Ensure the incoming JSON payload conforms to the expected schema.
3.  **Data Parsing:** Parse the JSON payload to extract the GNSS measurements, NMEA messages, and satellite status data.
4.  **Database Insertion:** Insert the parsed data into the appropriate database tables. The database schema should be designed to store the time-series GNSS data efficiently.

## 4. Database Schema

A simple database schema could look like this:

-   **stations**
    -   `id` (Primary Key)
    -   `station_id` (String, Unique)
    -   `name` (String)
    -   `location` (Geographic Point)

-   **gnss_measurements**
    -   `id` (Primary Key)
    -   `station_id` (Foreign Key to `stations`)
    -   `timestamp` (DateTime)
    -   ... (columns for all the fields in `raw.csv`)

-   **nmea_messages**
    -   `id` (Primary Key)
    -   `station_id` (Foreign Key to `stations`)
    -   `timestamp` (DateTime)
    -   `message` (Text)

-   **satellite_status**
    -   `id` (Primary Key)
    -   `station_id` (Foreign Key to `stations`)
    -   `timestamp` (DateTime)
    -   ... (columns for all the fields in `status.csv`)

## 5. Analysis and Processing

Once the data is in the database, you can perform various analyses, such as:

-   **Signal-to-Noise Ratio (SNR) Analysis:** Track the SNR of different satellites over time to assess signal quality.
-   **Multipath Detection:** Analyze the data to detect and mitigate multipath errors.
-   **Positioning Accuracy:** Calculate the positioning accuracy and compare it with known reference points.
-   **Atmospheric Studies:** Use the GNSS data to study the ionosphere and troposphere.

This documentation provides a high-level overview of the server setup. The specific implementation details will depend on your chosen technology stack.
