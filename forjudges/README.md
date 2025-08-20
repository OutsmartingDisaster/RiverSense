# RiverSense: A GNSS-IR System for Environmental Monitoring

RiverSense is a low-cost, near-real-time water level monitoring system designed to empower local communities at risk of unexpected flooding. Imagine an unused device in your drawer having the potential to prevent economic losses and even save lives. By repurposing everyday smartphones, RiverSense uses GNSS Interferometric Reflectometry (GNSS-IR) to provide a complete system for collecting and analyzing raw GNSS data for early-warning and environmental monitoring. The project consists of two main components:

1.  **An Android Application (`RiverSense-App`):** For collecting raw GNSS data from remote stations.
2.  **A Server Application (`RiverSense-Server`):** For processing the collected data, performing GNSS-IR analysis, and storing the results.

This document provides a high-level overview of the entire system. For more detailed information on each component, please refer to the `README.md` files in the respective subdirectories:

-   [`RiverSense-App/README.md`](RiverSense-App/README.md)
-   [`RiverSense-Server/README.md`](RiverSense-Server/README.md)

---

## RiverSense Android App

The RiverSense Android app is designed for logging raw GNSS data. It is a powerful tool for researchers, engineers, and hobbyists who need access to detailed GNSS measurements for post-processing and analysis.

### Key Features

-   **Raw GNSS Logging:** Captures detailed measurements, including pseudorange, carrier phase, and Doppler shift.
-   **NMEA & Status Logging:** Logs standard NMEA sentences and satellite status information.
-   **Manual & Station Modes:** Supports both on-demand (manual) and continuous (station) logging.
-   **Automated Data Uploads:** In station mode, the app automatically uploads data to the server every 5 minutes.
-   **Background Operation:** A foreground service ensures that logging continues even when the app is in the background.

---

## RiverSense Server

The RiverSense server is a complete solution for processing and analyzing GNSS data using GNSS-IR. It is designed to handle data uploads from remote stations, process the raw data, and store the results for further analysis.

### Key Features

-   **Data Reception:** A RESTful API for receiving GNSS data from the Android app.
-   **Asynchronous Processing:** A Celery-based worker system for handling data processing tasks in the background.
-   **GNSS-IR Analysis:** A processing pipeline for converting raw data to RINEX format, performing quality control, and calculating water levels using GNSS-IR.
-   **Containerized:** The entire server application is containerized using Docker, making it easy to deploy and manage.

## Getting Started

To get started with RiverSense, you will need to set up both the server and the Android app.

1.  **Set up the Server:** Follow the instructions in the [`RiverSense-Server/README.md`](RiverSense-Server/README.md) to build and run the server application.
2.  **Configure the App:** Follow the instructions in the [`RiverSense-App/README.md`](RiverSense-App/README.md) to configure the app to upload data to your server.

## Project Structure

```
.
├── RiverSense-App/     # Android application for data collection
└── RiverSense-Server/  # Server application for data processing