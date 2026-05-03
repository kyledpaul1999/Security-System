
import pytest
from unittest.mock import patch, MagicMock
from src.stream_processor.main import stream_camera

@pytest.mark.django_db
@patch('src.stream_processor.main.cv2')
@patch('src.stream_processor.main.start_ffmpeg_process')
@patch('src.stream_processor.main.LiveStream.objects')
def test_stream_camera_with_zeromq(mock_livestream_objects, mock_start_ffmpeg, mock_cv2):
    """
    Test that stream_camera runs, publishes frames to ZeroMQ, and cleans up.
    """
    camera_id = 'a-valid-uuid'
    rtsp_url = 'rtsp://test.url/stream'
    mock_socket = MagicMock()

    # Mock the ffmpeg process
    mock_ffmpeg_process = MagicMock()
    mock_start_ffmpeg.return_value = mock_ffmpeg_process

    # Mock the OpenCV capture
    mock_capture = MagicMock()
    mock_capture.isOpened.return_value = True
    mock_capture.read.side_effect = [(True, 'frame1'), (True, 'frame2'), (False, None)]
    mock_cv2.VideoCapture.return_value = mock_capture

    # Call the function
    stream_camera(camera_id, rtsp_url, mock_socket)

    # Assert that ffmpeg was started
    mock_start_ffmpeg.assert_called_once()

    # Assert that the LiveStream model was updated
    mock_livestream_objects.update_or_create.assert_called_once()

    # Assert that frames were published to ZeroMQ
    assert mock_socket.send_multipart.call_count == 2

    # Assert cleanup was performed
    mock_capture.release.assert_called_once()
    mock_ffmpeg_process.wait.assert_called_once()
    mock_livestream_objects.filter.assert_called_with(camera_id=camera_id)
    mock_livestream_objects.filter.return_value.delete.assert_called_once()

