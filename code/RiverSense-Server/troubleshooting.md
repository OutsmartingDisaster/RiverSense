# RiverSense Server Troubleshooting Guide

This guide provides a step-by-step approach to diagnosing and resolving common issues with the RiverSense server.

## 1. Verify the Server is Running

The first step in troubleshooting is to ensure that the server process is running. The specific command to do this will depend on how the server is being run (e.g., as a systemd service, in a Docker container, or directly from the command line).

-   **If running as a systemd service:**
    ```bash
    sudo systemctl status your-service-name
    ```
-   **If running in a Docker container:**
    ```bash
    docker ps
    ```
-   **If running from the command line:**
    ```bash
    ps aux | grep your-server-process
    ```

If the server is not running, try restarting it and check the logs for any startup errors.

## 2. Check Server Logs

Server logs are the most valuable resource for diagnosing issues. They will typically contain detailed information about incoming requests, errors, and other events. The location of the log files will depend on your server's configuration.

-   **Common log locations:**
    -   `/var/log/your-application-name/`
    -   `/var/log/syslog` or `journalctl` (for systemd services)
    -   Docker container logs (use `docker logs <container_id>`)

When examining the logs, look for any error messages, stack traces, or other unusual activity that coincides with the time of the failed request.

## 3. Test the API Endpoint

You can use a tool like `curl` to send test requests to the `/upload` endpoint. This will help you determine if the issue is with the server or the client.

-   **Create a test JSON file (`test.json`):**
    ```json
    {
      "station_id": "test-station",
      "timestamp": "2023-10-27T10:05:00Z",
      "data": {}
    }
    ```
-   **Send the request:**
    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d @test.json \
      http://your-server-address/api/v1/upload
    ```

If the `curl` command fails, the issue is likely with the server. If it succeeds, the issue may be with the client's network configuration or how it is constructing the request.

## 4. Database Connectivity

If the server is running but is unable to process requests, the issue may be with the database connection.

-   **Check the database server:** Ensure that the database server is running and accessible from the application server.
-   **Verify connection details:** Double-check the database connection string in your server's configuration to ensure that the host, port, username, password, and database name are all correct.
-   **Test the connection:** Most database systems provide a command-line client that you can use to test the connection from the application server.

## 5. Common Issues

-   **Incorrect JSON schema:** If the client is sending a JSON payload that does not conform to the schema, the server may return a 400 Bad Request or 500 Internal Server Error.
-   **Firewall rules:** Ensure that the server's firewall is configured to allow incoming traffic on the port that the application is listening on.
-   **Permissions:** The user that the server is running as must have the necessary permissions to write to log files and any other directories that it needs to access.
