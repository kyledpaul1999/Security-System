# Local-First AI Security System

This project is a comprehensive, locally hosted security system designed to replace commercial solutions like ADT Pulse. It integrates with existing IP cameras and NVRs to provide live monitoring, continuous recording, and real-time, AI-powered person detection.

Built with a modular, microservices-ready architecture, the system is designed for homelab or local server deployment first, ensuring that all sensitive video data remains on your private network by default.

For a complete technical overview, please see the [architecture.md](architecture.md) file.

## Key Features

- **Live Video Monitoring**: View camera streams in real-time through a web or mobile client.
- **Continuous & Triggered Recording**: Supports scheduled, manual, motion-triggered, and AI-powered recording.
- **AI-Powered Person Detection**: Uses YOLOv8 to run real-time person detection on video streams, with configurable detection zones and confidence thresholds.
- **Rich Automation**: A powerful rules engine allows for custom automations based on events (e.g., "if a person is detected at the front door after 10 PM, send a notification and start a 60-second recording").
- **Notifications**: Receive alerts via mobile push, email, or webhooks.
- **Secure Remote Access**: A VPN-first approach ensures that your system is not exposed to the public internet.
- **Local Data Storage**: All video clips, recordings, and event metadata are stored on your local infrastructure.
- **Audit Trails**: Maintains a clear audit log for user actions, detections, and system events.

## System Architecture

The system uses a hybrid architecture that combines a core **Django monolith** with several specialized **Python microservices** for data processing. This design provides the rapid development of a monolith for the main API while isolating resource-intensive tasks into scalable, independent services.

The primary services, orchestrated with Docker Compose, are:

-   `api`: A Django-based monolith that serves the primary REST API for the web and mobile clients. It manages users, cameras, recordings, automation rules, and more.
-   `stream_processor`: Connects to RTSP-enabled cameras, captures video frames, and publishes them to a ZeroMQ message queue.
-   `person_detector`: Subscribes to the frame queue, runs person detection using a YOLOv8 model, and publishes detection events.
-   `event_handler`: Subscribes to detection events, stores them in the database, and can trigger further actions.
-   `timescaledb`: A PostgreSQL database with the TimescaleDB extension, used as the primary data store for all system metadata and events.
-   `redis`: Used for caching, session management, and managing the state of background tasks.

## Technology Stack

-   **Backend**: Django 4.2, Python 3.9
-   **AI / ML**: PyTorch, YOLOv8, OpenCV
-   **Database**: PostgreSQL with TimescaleDB
-   **Messaging**: ZeroMQ
-   **Caching**: Redis
-   **Infrastructure**: Docker & Docker Compose

## Getting Started

### Prerequisites

-   Docker and Docker Compose must be installed on your system.
-   You need access to one or more RTSP video streams from your IP cameras or NVR.

### Configuration

1.  **Docker Compose**: The primary configuration is handled via environment variables in the `docker-compose.yml` file. You may need to adjust the RTSP URLs for the `stream_processor` service to match your cameras.

2.  **Database Initialization**: The `timescaledb` service will be initialized automatically on the first run. The Django `api` service is configured to run database migrations automatically on startup, ensuring the schema is always up-to-date.

### Running the System

To build the Docker images and start all the services, run the following command from the project root:

```bash
docker-compose up --build
```

This will:
1.  Build the Docker images for each service.
2.  Start all the containers defined in `docker-compose.yml`.
3.  Automatically run Django database migrations.
4.  Begin processing the configured video streams.

You can view the logs for a specific service using:
```bash
docker-compose logs -f <service_name>
```
(e.g., `api`, `stream_processor`, `person_detector`)

### Stopping the System

To stop all running containers, press `Ctrl+C` in the terminal where Docker Compose is running, or execute:

```bash
docker-compose down
```
