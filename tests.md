# Comprehensive Testing Guide

This document provides a complete guide to testing the security system, from running automated unit and integration tests to performing manual end-to-end (E2E) functional verification.

## 1. Running Automated Tests

Automated tests are the first line of defense against regressions. They should be run frequently during development.

### Django `api` Service Tests

These tests cover the database models and the core API endpoints.

```bash
# From the project root directory
docker-compose exec api pytest
```

*   **What it tests:**
    *   **Model Logic:** Ensures database relationships, constraints, and custom methods work as expected (e.g., `test_cameras_models.py`).
    *   **API Endpoints:** Verifies the CRUD operations for our core resources (e.g., `test_cameras_api.py`, `test_recordings_api.py`).

### Node.js `gateway` Service Tests

These tests cover the critical middleware of our API Gateway.

```bash
# From the /Users/kylepaul/Projects/Security-System/src/gateway/ directory
npm install
npm test
```

*   **What it tests:**
    *   **Authentication:** Confirms that our JWT middleware correctly validates tokens and protects routes.
    *   **Proxying:** Ensures that the gateway is correctly configured to forward requests.

### Python `stream_processor` and `event_handler` Tests

These tests can be run from within the `api` service container, as they share the same Python environment.

```bash
# From the project root directory
docker-compose exec api pytest src/stream_processor/
docker-compose exec api pytest src/event_handler/
```

*   **What it tests:**
    *   **Streaming Logic:** Verifies that the `stream_processor` correctly initiates FFmpeg and publishes frames to ZeroMQ.
    *   **Alert Routing:** Ensures the `event_handler` correctly evaluates rules and dispatches actions.

---

## 2. Manual End-to-End (E2E) Functional Testing

After the automated tests pass, this phase ensures all services work together correctly.

### Setup: Start the System

1.  **Start all services:**
    ```bash
    docker-compose up --build -d
    ```
2.  **Run database migrations:** This creates the database schema and runs the data seeding migration.
    ```bash
    docker-compose exec api python manage.py migrate
    ```

### Test Case 1: User Login and Camera Registration

1.  **Get an Auth Token:** Use `curl` or Postman to log in as the default admin user created by the seeder.
    ```bash
    # This will return an access token
    curl -X POST http://localhost:8000/api/auth/login/ \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "password"}'
    ```
2.  **Register a Camera:** Using the token from the previous step, register a camera. **You must use a real, valid RTSP URL from your network for this to work.**
    ```bash
    curl -X POST http://localhost:8000/api/cameras/ \
      -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{
            "name": "Live Test Camera",
            "channel_no": 1,
            "rtsp_main_url": "rtsp://your-actual-camera-url"
          }'
    ```
    *   **Expected Result:** You get a `201 Created` response.

### Test Case 2: Live Video Playback

1.  **Check Service Logs:** Check the logs of the `stream_processor` to confirm it has started streaming the new camera.
    ```bash
    docker-compose logs -f stream_processor
    ```
    *   **Expected Result:** You should see a log message like `Starting stream for camera <camer-id>...`.
2.  **Play the HLS Stream:** The HLS manifest URL will be `http://localhost:8080/hls/<camer-id>/index.m3u8`. The port `8080` is mapped by the `nginx` service.
    *   Open this URL in a media player that supports HLS (e.g., VLC Media Player, QuickTime on macOS, or an online HLS player).
    *   **Expected Result:** The live video stream from your camera should start playing.

### Test Case 3: Event and Alerting Pipeline (Advanced)

This test verifies that the event system can trigger actions. It requires a webhook receiver.

1.  **Set up a Webhook Receiver:** Use a service like [webhook.site](https://webhook.site/) or `ngrok` to get a publicly accessible URL that can receive POST requests.
2.  **Update the Automation Rule:** The data seeder created a sample rule. Use the API to find its ID and update its action to point to your webhook URL.
3.  **Trigger a Detection (Simulated):** Since the AI service is not yet complete, you can simulate a detection event by manually publishing a message to the ZeroMQ topic. This is an advanced step for isolated testing.
4.  **Check Your Webhook Receiver:**
    *   **Expected Result:** Your webhook receiver should receive a POST request containing the JSON payload of the simulated detection event, proving the `event_handler` is working correctly.
