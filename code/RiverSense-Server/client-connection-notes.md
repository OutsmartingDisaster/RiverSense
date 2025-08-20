# Client Connection Notes

This document provides instructions for connecting a client application to the RiverSense server.

## Authentication

All API requests must include an `Authorization` header for authentication.

-   **Header**: `Authorization`
-   **Value**: `Bearer riversense`

## API Endpoint

The base URL for the file upload API endpoint is:

-   `/api/v1/upload`

## Connection Scenarios

Below are `curl` examples for connecting to the server in different network environments.

### 1. Local Network

Use this command when the client is on the same local network as the server.

```bash
curl -X POST -H "Authorization: Bearer riversense" -F "file=@/path/to/your/file" http://192.168.18.71:8002/api/v1/upload
```

### 2. Tailscale

Use this command when connecting through a Tailscale VPN.

```bash
curl -X POST -H "Authorization: Bearer riversense" -F "file=@/path/to/your/file" http://100.71.125.39:8002/api/v1/upload
```

### 3. Custom Domain

If you have a custom domain pointing to the server, use the following format.

**Note**: Ensure your custom domain's DNS records are configured to point to the server's public IP address, and traffic to port `8002` is correctly forwarded.

```bash
curl -X POST -H "Authorization: Bearer riversense" -F "file=@/path/to/your/file" https://your-custom-domain.com/api/v1/upload