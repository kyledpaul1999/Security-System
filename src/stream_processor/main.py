import os
import time
import threading

import os
import time
import threading
import psycopg2
import cv2
import zmq
import ffmpeg

import requests

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def get_cameras():
    """Fetches all enabled cameras from the database using a direct DB connection."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, rtsp_main_url FROM cameras_camera WHERE is_enabled = TRUE")
    cameras = cur.fetchall()
    cur.close()
    conn.close()
    return cameras

def start_ffmpeg_process(rtsp_url, hls_output_path):
    try:
        process = (
            ffmpeg.input(rtsp_url, rtsp_transport='tcp', use_wallclock_as_timestamps=1)
            .output(
                hls_output_path,
                format='hls',
                hls_time=10,
                hls_list_size=6,
                hls_flags='delete_segments',
                vcodec='copy',
                acodec='copy'
            )
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
        return process
    except Exception as e:
        print(f"Error starting FFmpeg: {e}")
        return None

def stream_camera(camera_id, rtsp_url, zmq_socket):
    """
    Connects to a single RTSP stream, publishes frames to ZeroMQ, and
    transcodes the stream to HLS.
    """
    print(f"Starting stream for camera {camera_id} at {rtsp_url}")

    # --- HLS Conversion ---
    hls_output_dir = f"/media/hls/{camera_id}"
    os.makedirs(hls_output_dir, exist_ok=True)
    hls_output_path = f"{hls_output_dir}/index.m3u8"

    ffmpeg_process = start_ffmpeg_process(rtsp_url, hls_output_path)
    if not ffmpeg_process:
        return

    # Notify the API that the stream is active
    try:
        requests.post(
            f"http://api:8000/api/recordings/livestream-status/",
            json={
                "camera": camera_id,
                "status": "active",
                "hls_manifest_path": hls_output_path,
                "stream_profile": "main",
            },
        )
    except requests.exceptions.RequestException as e:
        print(f"Error notifying API of active stream for camera {camera_id}: {e}")

    # --- ZeroMQ Frame Publishing ---
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"Error: Could not open RTSP stream for camera {camera_id}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        zmq_socket.send_multipart([f"camera.{camera_id}".encode(), buffer.tobytes()])

    cap.release()
    ffmpeg_process.wait()
    print(f"Stopped stream for camera {camer-id}")

    # Notify the API that the stream has stopped
    try:
        requests.delete(f"http://api:8000/api/recordings/livestream-status/{camera_id}/")
    except requests.exceptions.RequestException as e:
        print(f"Error notifying API of stopped stream for camera {camera_id}: {e}")

def main():
    """
    Main function to set up the ZeroMQ publisher and start streaming threads for each camera.
    """
    print("Starting Stream Processor Service...")

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.bind("tcp://*:5555")

    cameras = get_cameras()
    if not cameras:
        print("No enabled cameras found. Shutting down.")
        return

    for camera in cameras:
        thread = threading.Thread(target=stream_camera, args=(camera[0], camera[1], zmq_socket))
        thread.daemon = True
        thread.start()

    print(f"Started {len(cameras)} camera streaming threads.")

    try:
        while True:
            time.sleep(60)
            print("Stream processor is running...")
    except KeyboardInterrupt:
        print("Shutting down stream processor.")

if __name__ == "__main__":
    time.sleep(10) # Wait for the DB to be ready
    main()
