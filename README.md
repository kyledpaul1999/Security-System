# Real-Time AI Object Detection Security System

This project is a real-time AI object detection security system that uses RTSP streams, PyTorch, YOLOv8, ZeroMQ, and TimescaleDB. It is designed with a microservice architecture and is orchestrated using Docker Compose.

## Project Architecture

The system is composed of three main microservices:

1.  **Stream Processor**: Connects to RTSP-enabled cameras, captures video frames, and publishes them to a ZeroMQ message queue.
2.  **Person Detector**: Subscribes to the frame queue, performs object detection using the YOLOv8 model, and publishes detection events to another ZeroMQ queue.
3.  **Event Handler**: Subscribes to the detection event queue, stores the events in a TimescaleDB database, and contains placeholder logic for sending alerts.

This architecture is designed for scalability and maintainability. Each service can be developed, deployed, and scaled independently.

### Performance Optimization

To ensure the system runs efficiently, even with multiple high-resolution camera streams, a motion-based detection filter has been implemented in the `person_detector` service. Here’s how it works:

-   **Background Subtraction**: The service uses OpenCV’s background subtraction capabilities to identify areas of motion in each frame.
-   **Motion Filtering**: The YOLOv8 person detection model is only run on frames where significant motion is detected. This dramatically reduces the computational load on the GPU/CPU.
-   **Adjustable Sensitivity**: The sensitivity of the motion detection can be tuned via the `MIN_CONTOUR_AREA` environment variable in the `docker-compose.yml` file, allowing you to customize it for your specific environment.

This optimization ensures that your system's resources are used intelligently, focusing only on the frames that matter.

### System Components

-   **Docker & Docker Compose**: For containerizing and orchestrating the application services.
-   **Python**: The primary language for all microservices.
-   **OpenCV**: Used for video capture and image processing.
-   **PyTorch & YOLOv8**: For performing real-time object detection.
-   **ZeroMQ**: A high-performance asynchronous messaging library for communication between services.
-   **TimescaleDB**: A time-series SQL database for storing detection events, built on PostgreSQL.
-   **React (Future)**: The project structure includes a placeholder for a future web-based user interface.

## Getting Started

### Prerequisites

-   Docker and Docker Compose installed.
-   Access to one or more RTSP video streams from IP cameras.

### Configuration

Before launching the system, you need to configure the camera streams.

1.  **Database**: The `database/init.sql` file is pre-configured to create the necessary tables and add three sample cameras. You should update the `rtsp_url` values in this file to match your camera streams. You can also add or remove cameras as needed.

2.  **Docker Compose**: The `docker-compose.yml` file defines the services. You can modify the environment variables in this file if needed, but the defaults should work for a local setup.

### Running the System

Once configured, you can start the entire system with a single command:

```bash
docker-compose up --build
```

This command will:

1.  Build the Docker images for each microservice.
2.  Start the TimescaleDB container and initialize the database using the `init.sql` script.
3.  Start the `stream_processor`, `object_detector`, and `event_handler` services.

You can view the logs for each service in a separate terminal:

```bash
docker-compose logs -f <service_name>
```

Replace `<service_name>` with `stream_processor`, `person_detector`, or `event_handler`.

To stop the system, press `Ctrl+C` in the terminal where `docker-compose up` is running, or run:

```bash
docker-compose down
```

## Database Schema

The database schema is designed to be lean and efficient for time-series data.

-   `cameras`: Stores information about each camera, including its name and RTSP URL.
-   `detection_events`: A TimescaleDB hypertable that stores every object detection event. It is partitioned by time for fast querying and includes details like the camera, detected object label, confidence score, and bounding box coordinates.

## Future Development

The `frontend` directory is a placeholder for a React application that will provide a user interface for viewing camera streams and detection events. The `event_handler` service can be extended to include a REST API to serve data to the frontend.
