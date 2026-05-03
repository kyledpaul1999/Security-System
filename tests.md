Of course. Testing these interconnected features requires a combination of automated tests and some manual, functional testing to see everything working together. Here’s a detailed guide on how you can approach testing for each of the functionalities you mentioned.

### **1. Camera Registration**

Camera registration is the process of adding a new camera to the system. This can be tested at both the API level (integration testing) and through manual HTTP requests.

#### **Automated Testing (Integration Tests)**

The best way to test this automatically is with an API integration test. I have already created a test suite for the camera API that does exactly this.

*   **File:** [`test_cameras_api.py`](file:///Users/kylepaul/Projects/Security-System/src/api/cameras/test_cameras_api.py)
*   **Key Test:** `test_create_camera`

Here is the relevant snippet from that file:

```python
# src/api/cameras/test_cameras_api.py

def test_create_camera(self, authenticated_client):
    """Test creating a new camera."""
    data = {
        'name': 'New Camera',
        'channel_no': 3
    }
    
    response = authenticated_client.post('/cameras/', data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Camera.objects.count() == 1
    assert Camera.objects.get().name == 'New Camera'
```

This test uses `pytest` and Django REST Framework's `APIClient` to make a `POST` request to the `/cameras/` endpoint and asserts that a new camera is created in the database.

#### **Manual Functional Testing**

You can also test this manually using a tool like `curl` or Postman.

1.  **Start the services:**
    ```bash
    docker-compose up -d
    ```
2.  **Get an auth token:** You'll first need to log in as the admin user to get a JWT.
3.  **Make a `POST` request:**
    ```bash
    curl -X POST http://localhost:8000/api/cameras/ \
      -H "Authorization: Bearer <YOUR_JWT>" \
      -H "Content-Type: application/json" \
      -d '{
            "name": "My New Camera",
            "channel_no": 4,
            "rtsp_main_url": "rtsp://your-stream-url"
          }'
    ```
    You should receive a `201 Created` response.

---

### **2. RTSP Stream Discovery**

In the current implementation, RTSP stream "discovery" is a manual process. The user is expected to provide the correct RTSP URL when registering a camera. The `architecture.md` mentions ONVIF for future automatic discovery, but that is not yet implemented.

Therefore, testing this is about ensuring that the `stream_processor` correctly uses the `rtsp_main_url` that is saved in the `Camera` model.

#### **Automated Testing (Unit Tests)**

The unit test for the `stream_processor` that I created mocks out the RTSP URL and the `ffmpeg` process. This test verifies that the `stream_camera` function is called with the correct RTSP URL from the `Camera` object.

*   **File:** [`test_main.py`](file:///Users/kylepaul/Projects/Security-System/src/stream_processor/test_main.py)

This test ensures that the correct URL is being passed to the streaming logic.

---

### **3. HLS Playback**

HLS playback is best tested functionally, as it involves multiple services working together (`api`, `stream_processor`, and `nginx`).

#### **Manual Functional Testing**

1.  **Start the services:**
    ```bash
    docker-compose up -d
    ```
2.  **Register a camera:** Use the manual `curl` command from above to register a camera with a **valid** RTSP stream URL.
3.  **Verify the stream is running:** You should see logs in the `stream_processor` container indicating that it has started streaming the camera.
4.  **Play the HLS stream:** The HLS manifest will be available at a URL like `http://localhost:8080/hls/<camer-id>/index.m3u8`. The `8080` port is based on the `nginx` service in the `docker-compose.yml` file. You can open this URL in a media player that supports HLS, such as:
    *   **VLC Media Player:** Go to `File > Open Network...` and paste the URL.
    *   **Online HLS Players:** There are several websites that can play HLS streams if you provide the URL.

If the stream plays, you have successfully verified that RTSP ingestion and HLS transcoding are working correctly.

---

### **4. Recording Metadata**

Similar to camera registration, recording metadata can be tested with both automated integration tests and manual API requests.

#### **Automated Testing (Integration Tests)**

I have also created a test suite for the recording API.

*   **File:** [`test_recordings_api.py`](file:///Users/kylepaul/Projects/Security-System/src/api/recordings/test_recordings_api.py)
*   **Key Tests:** `test_create_recording` and `test_retrieve_recording`

Here is a snippet:

```python
# src/api/recordings/test_recordings_api.py

def test_create_recording(self, authenticated_client, camera_fixture):
    """Test creating a new recording."""
    data = {
        'camera': camera_fixture.id,
        'recording_type': 'manual',
        'start_time': timezone.now(),
        'end_time': timezone.now() + timezone.timedelta(minutes=5),
        'object_prefix': 'rec/new/',
        'duration_seconds': 300
    }
    
    response = authenticated_client.post('/recordings/', data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Recording.objects.count() == 1
```

This test verifies that you can create a new recording via the API and that the metadata is saved to the database.

#### **Manual Functional Testing**

You can use `curl` to create and retrieve recording metadata.

1.  **Create a recording:**
    ```bash
    curl -X POST http://localhost:8000/api/recordings/ \
      -H "Authorization: Bearer <YOUR_JWT>" \
      -H "Content-Type: application/json" \
      -d '{
            "camera": "<your_camer-id>",
            "recording_type": "manual",
            "start_time": "2026-05-02T10:00:00Z",
            "end_time": "2026-05-02T10:05:00Z",
            "object_prefix": "rec/manual/",
            "duration_seconds": 300
          }'
    ```
2.  **Retrieve the recording:** After creating it, you can fetch its metadata:
    ```bash
    curl http://localhost:8000/api/recordings/<recording_id>/ \
      -H "Authorization: Bearer <YOUR_JWT>"
    ```
    This should return the JSON object with all the metadata for that recording.

By combining these automated and manual testing approaches, you can have high confidence that these core features are working as expected.
