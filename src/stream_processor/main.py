import os
import time
import threading

# --- Django Setup ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.api.core.settings')
import django
django.setup()
# --- End Django Setup ---

import cv2
import zmq
import ffmpeg
from src.api.cameras.models import Camera
from src.api.recordings.models import LiveStream

def get_cameras():
    """Fetches all enabled cameras from the database using the Django ORM."""
    return Camera.objects.filter(is_enabled=True)

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

    LiveStream.objects.update_or_create(
        camera_id=camera_id,
        defaults={
            'status': 'active',
            'hls_manifest_path': hls_output_path,
            'stream_profile': 'main'
        }
    )

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
    LiveStream.objects.filter(camera_id=camera_id).delete()
    print(f"Stopped stream for camera {camera_id}")

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
        thread = threading.Thread(target=stream_camera, args=(camera.id, camera.rtsp_main_url, zmq_socket))
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
