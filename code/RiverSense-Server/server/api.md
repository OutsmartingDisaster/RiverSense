# RiverSense Server API

This document provides a detailed description of the RiverSense server API.

## Upload Endpoint

-   **Endpoint:** `/upload`
-   **Method:** `POST`
-   **Content-Type:** `application/json`

### JSON Payload Schema

The body of the request should be a JSON object with the following structure:

```json
{
  "station_id": "station-001",
  "timestamp": "2023-10-27T10:05:00Z",
  "data": {
    "raw": [
      {
        "UTCTimeMillis": 1698397800000,
        "TimeNanos": 1234567890,
        "FullBiasNanos": 9876543210,
        "Svid": 1,
        "Cn0DbHz": 35.5,
        "...": "..."
      }
    ],
    "nmea": [
      {
        "timestamp": 1698397800000,
        "message": "$GPGGA,..."
      }
    ],
    "status": [
      {
        "TimeMillis": 1698397800000,
        "Svid": 1,
        "Cn0DbHz": 35.5,
        "ConstellationType": 1,
        "ElevationDegrees": 45.0,
        "AzimuthDegrees": 120.0,
        "UsedInFix": true
      }
    ]
  }
}
```

### Example Request

Here's an example of how to make a request using `curl`:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @/path/to/your/data.json \
  http://your-server-address/upload
```

### Success Response

-   **Status Code:** `200 OK`
-   **Body:**

```json
{
  "status": "success",
  "message": "Data for station-001 at 2023-10-27T10:05:00Z received."
}
```

### Error Responses

-   **Status Code:** `400 Bad Request` (e.g., missing parameters)
-   **Body:**

```json
{
  "status": "error",
  "message": "Missing required parameter: station_id"
}
```

-   **Status Code:** `500 Internal Server Error` (e.g., processing failure)
-   **Body:**

```json
{
  "status": "error",
  "message": "Failed to process uploaded data."
}
