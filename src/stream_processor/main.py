
import cv2
import zmq
import os
import time
import threading
import psycopg2
from psycopg2 import OperationalError

# This service connects to RTSP streams, captures frames, and publishes them using ZeroMQ.
# It's designed to be resilient, attempting to reconnect to streams and the database if connections are lost.

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.
    This function will retry connection attempts for a short period if the database
    is not immediately available, which is common in containerized environments.
    """
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            print("Database connection successful.")
            return conn
        except OperationalError as e:
            print(f"Database connection failed: {e}")
            retries -= 1
            print(f"Retrying connection in 5 seconds... ({retries} retries left)")
            time.sleep(5)
    print("Could not establish database connection after several retries. Exiting.")
    return None

def get_cameras(conn):
    """
    Fetches camera information (ID and RTSP URL) from the database.
    This allows for dynamic configuration of video streams without changing the code.
    """
    if conn is None:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, rtsp_url FROM cameras")
            cameras = cur.fetchall()
            print(f"Found {len(cameras)} cameras in the database.")
            return cameras
    except psycopg2.Error as e:
        print(f"Error fetching cameras: {e}")
        return []

def stream_camera(camera_id, rtsp_url, zmq_socket):
    """
    Connects to a single RTSP stream, captures frames, and publishes them.
    This function runs in a separate thread for each camera.
    If the stream connection is lost, it will attempt to reconnect.
    """
    print(f"Starting stream for camera {camera_id} at {rtsp_url}")
    while True:
        # Attempt to connect to the video stream
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            print(f"Error: Could not open stream for camera {camera_id}. Retrying in 10 seconds.")
            time.sleep(10)
            continue

        print(f"Successfully connected to stream for camera {camera_id}.")
        while cap.isOpened():
            # Read a frame from the stream
            ret, frame = cap.read()
            if not ret:
                print(f"Stream for camera {camera_id} ended. Reconnecting...")
                break  # Exit inner loop to trigger reconnection

            # Publish the frame to the object detector service
            # The message is sent in two parts: the camera ID and the frame data
            # The frame is encoded as a JPEG for efficient network transmission
            _, buffer = cv2.imencode('.jpg', frame)
            zmq_socket.send_multipart([str(camera_id).encode(), buffer.tobytes()])

        cap.release()
        print(f"Released video capture for camera {camera_id}.")
        time.sleep(5) # Wait a moment before attempting to reconnect

def main():
    """
    Main function to set up the ZeroMQ publisher and start streaming threads for each camera.
    """
    print("Starting Stream Processor Service...")

    # Set up ZeroMQ publisher socket
    # This socket will broadcast frames to any connected subscribers (the object detector)
    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.PUB)
    zmq_pub_url = os.getenv("ZMQ_PUB_URL", "tcp://*:5555")
    zmq_socket.bind(zmq_pub_url)
    print(f"ZeroMQ publisher bound to {zmq_pub_url}")

    # Get database connection and camera information
    db_conn = get_db_connection()
    cameras = get_cameras(db_conn)
    if db_conn:
        db_conn.close()

    if not cameras:
        print("No cameras found. Shutting down.")
        return

    # Start a thread for each camera to handle its stream independently
    threads = []
    for camera_id, rtsp_url in cameras:
        thread = threading.Thread(target=stream_camera, args=(camera_id, rtsp_url, zmq_socket))
        thread.daemon = True  # Allows main thread to exit even if camera threads are running
        threads.append(thread)
        thread.start()

    print(f"Started {len(threads)} camera streaming threads.")
    
    # Keep the main thread alive to allow daemon threads to run
    try:
        while True:
            time.sleep(60)
            print("Stream processor is running...")
    except KeyboardInterrupt:
        print("Shutting down stream processor.")

    # Clean up ZeroMQ resources
    zmq_socket.close()
    zmq_context.term()
    print("Stream processor shut down.")

if __name__ == "__main__":
    main()
