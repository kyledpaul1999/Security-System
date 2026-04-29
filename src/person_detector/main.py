
import zmq
import numpy as np
import cv2
import torch
from ultralytics import YOLO
import os
import json
import time

# This service is the heart of the AI-powered security system. It performs the following key functions:
#
# 1.  **Motion-Based Frame Filtering**: To optimize performance and reduce unnecessary computation,
#     the service first analyzes incoming video frames for significant motion. It uses a background
#     subtraction algorithm to detect changes between frames. This ensures that the resource-intensive
#     person detection model is only run when there is activity in the camera's view.
#
# 2.  **Person Detection**: When significant motion is detected, the service uses the powerful YOLOv8
#     (You Only Look Once) model to scan the frame for the presence of people. YOLOv8 is a state-of-the-art,
#     real-time object detection model, and we are specifically using it to identify persons.
#
# 3.  **Event Publishing**: If a person is detected, the service generates a detailed detection event.
#     This event, formatted as a JSON object, includes the camera ID, a timestamp, the label ('person'),
#     the model's confidence score, and the bounding box coordinates of the detected person. This event
#     is then published to a ZeroMQ topic for other services to consume (like the event_handler).
#
# This combination of motion filtering and targeted person detection creates an efficient and effective
# security monitoring pipeline.

def main():
    """
    Main function to initialize and run the person detection service.
    This function sets up the YOLOv8 model, initializes ZeroMQ for communication,
    prepares the motion detection filters, and enters a continuous loop to process video frames.
    """
    print("Starting Person Detector Service with Motion-Based Optimization...")

    # --- Device Configuration ---
    # Determine the best available device for running the YOLOv8 model.
    # Using a CUDA-enabled GPU ('cuda') will provide a significant performance boost,
    # which is crucial for real-time video analysis. If no GPU is available, it falls back to the CPU ('cpu').
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # --- Model Loading ---
    # Load the pre-trained YOLOv8 model. We are using 'yolov8n.pt', the nano version,
    # which is the smallest and fastest variant, making it ideal for real-time applications
    # where speed is more critical than achieving the highest possible accuracy.
    try:
        model = YOLO('yolov8n.pt')
        model.to(device)  # Move the model to the selected device (GPU or CPU)
        print("YOLOv8 model loaded successfully.")
    except Exception as e:
        print(f"Error loading YOLOv8 model: {e}")
        return

    # --- ZeroMQ Initialization ---
    # Initialize the ZeroMQ context and sockets for inter-service communication.
    zmq_context = zmq.Context()

    # Subscriber Socket: This socket connects to the 'stream_processor' service to receive
    # raw video frames as they are captured from the RTSP streams.
    sub_socket = zmq_context.socket(zmq.SUB)
    sub_socket.subscribe(b'')  # Subscribe to all messages from the publisher
    zmq_sub_url = os.getenv("ZMQ_SUB_URL", "tcp://localhost:5555")
    sub_socket.connect(zmq_sub_url)
    print(f"ZeroMQ subscriber connected to {zmq_sub_url}")

    # Publisher Socket: This socket is used to broadcast the detection events (as JSON objects)
    # to any services that need to know about them, primarily the 'event_handler' service.
    pub_socket = zmq_context.socket(zmq.PUB)
    zmq_pub_url = os.getenv("ZMQ_PUB_URL", "tcp://*:5556")
    pub_socket.bind(zmq_pub_url)
    print(f"ZeroMQ publisher bound to {zmq_pub_url}")

    # --- Motion Detection Setup ---
    # A dictionary to hold a separate background subtractor for each camera stream.
    # This is essential because motion needs to be tracked independently for each camera's unique view.
    background_subtractors = {}
    # The minimum size (in pixels) a moving object must be to be considered 'significant motion'.
    # This helps to filter out minor environmental changes like rustling leaves or camera noise.
    # This value can be tuned via an environment variable for different camera setups.
    MIN_CONTOUR_AREA = int(os.getenv("MIN_CONTOUR_AREA", 500))

    print("Person detector is ready and waiting for frames...")
    try:
        # --- Main Processing Loop ---
        # This is the core of the service, a continuous loop that receives frames, checks for motion,
        # and runs the person detection model when needed.
        while True:
            # Receive a frame from the stream_processor. The message is multipart, containing
            # the camera ID and the raw JPEG-encoded frame data.
            camera_id, frame_bytes = sub_socket.recv_multipart()
            camera_id = camera_id.decode('utf-8')

            # Decode the JPEG data into a NumPy array that OpenCV can process.
            frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

            if frame is None:
                print(f"Received an empty or invalid frame for camera {camera_id}. Skipping.")
                continue

            # --- Motion Detection Pre-Filter ---
            # If this is the first frame from a camera, create a background subtractor for it.
            if camera_id not in background_subtractors:
                # We use the MOG2 background subtraction algorithm, which is robust and widely used.
                background_subtractors[camera_id] = cv2.createBackgroundSubtractorMOG2(
                    history=500, varThreshold=50, detectShadows=True)
                print(f"Initialized background subtractor for camera {camera_id}")

            # Apply the background subtractor to the current frame to get a foreground mask.
            # This mask highlights the pixels that have changed, i.e., where motion has occurred.
            fg_mask = background_subtractors[camera_id].apply(frame)

            # Find the distinct moving objects (contours) in the foreground mask.
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if any of the detected contours are large enough to be considered significant.
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
                    motion_detected = True
                    break  # Exit early as soon as one significant motion is found

            # If no significant motion is found, skip the expensive AI inference step.
            if not motion_detected:
                continue

            print(f"Significant motion detected on camera {camera_id}. Running person detection...")
            # --- Person Detection ---
            # Perform person detection on the frame using the YOLOv8 model.
            # The 'predict' method handles all the complex parts of the inference.
            results = model.predict(frame, device=device, verbose=False) # verbose=False keeps the logs clean

            # Process the results to find any 'person' detections.
            for result in results:
                if result.boxes:
                    for box in result.boxes:
                        label = model.names[int(box.cls[0])]
                        # This is the critical filter: we only care about detections labeled as a 'person'.
                        if label == 'person':
                            # Extract the bounding box coordinates and the confidence score.
                            x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]
                            confidence = float(box.conf[0])

                            # Assemble the detection event data into a dictionary.
                            detection_event = {
                                "camera_id": camera_id,
                                "time": time.time(),  # Use a Unix timestamp for the event time
                                "label": label,
                                "confidence": confidence,
                                "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                            }
                            # Publish the event to the ZeroMQ topic for the event_handler to process.
                            pub_socket.send_json(detection_event)

    except KeyboardInterrupt:
        print("Shutting down person detector.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # --- Cleanup ---
        # Gracefully close the ZeroMQ sockets and terminate the context to free up resources.
        sub_socket.close()
        pub_socket.close()
        zmq_context.term()
        print("Person detector shut down.")

if __name__ == "__main__":
    main()
