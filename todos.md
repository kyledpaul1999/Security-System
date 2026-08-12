# Project To-Do List

This document outlines the remaining configuration and implementation tasks needed to get the security system project fully running as per the `architecture.md` file. It is divided into sections for local setup, one-time configuration, and feature implementation.

---

## 1. Local Environment Setup

These are tasks that you need to perform once on your local machine to ensure your development environment is ready.

- [ ] **Install and Configure `nvm`**
  - **Why**: To manage your Node.js versions and provide IDE support for the API Gateway.
  - **Action**: You were given manual instructions for this. You need to run the `echo` command to update your `~/.zshrc` file, then restart your terminal.

- [ ] **Install Node.js**
  - **Why**: Required by your IDE for TypeScript language support.
  - **Action**: After setting up `nvm`, run `nvm install 16` and `nvm use 16` in your terminal.

- [ ] **Install Local `npm` Dependencies**
  - **Why**: To give your IDE code completion and error checking for the gateway.
  - **Action**: Navigate to the `src/gateway` directory and run `npm install`.

---

## 2. One-Time Project Configuration

These tasks need to be done once to initialize the project's services.

- [ ] **Create the MinIO Storage Bucket**
  - **Why**: The storage bucket must exist before the application can save files to it.
  - **Action**: 
    1. Run `docker-compose up -d` to start all services.
    2. Open a browser to the MinIO console at `http://localhost:9001`.
    3. Log in with `minioadmin` / `minioadmin`.
    4. Create a new bucket named `security-system`.

- [ ] **Run Initial Database Migrations**
  - **Why**: To create the database tables required by the Django `api` service.
  - **Action**: Once the `timescaledb` container is running and healthy, run the following command:
    ```bash
    docker-compose exec api python manage.py migrate
    ```

---

## 3. Core Feature Implementation

These are the major remaining implementation tasks to make the system fully functional.

- [x] **API Gateway: Implement JWT Validation**
- [x] **API Gateway: Implement RBAC Enforcement (Placeholder)**
- [x] **API Gateway: Implement Rate Limiting**
- [x] **API Gateway: Implement Correlation IDs**
- [x] **API Gateway: Implement Health Check Endpoint**
- [x] **API: Implement Camera and NVR Registration**
- [x] **API: Implement Basic Recording Metadata Endpoints**

- [ ] **`stream_processor`: Implement HLS Transcoding**
  - **Why**: The current implementation is a placeholder. It needs to use `ffmpeg` to actively transcode the incoming RTSP stream into HLS segments and a manifest file.
  - **File**: `src/stream_processor/main.py`
  - **Action**: In the `stream_camera` function, replace the placeholder comment with a call to `ffmpeg-python` to start the transcoding process. This process should run in the background for the duration of the stream.

- [ ] **`stream_processor`: Implement ZeroMQ Frame Publishing**
  - **Why**: The logic to publish video frames to ZeroMQ for the `person_detector` service was removed during the last refactoring and needs to be re-integrated.
  - **File**: `src/stream_processor/main.py`
  - **Action**: Inside the `stream_camera` function, add the logic to capture frames from the RTSP stream (using OpenCV), encode them as JPEGs, and publish them to a ZeroMQ topic.

- [ ] **`event_handler`: Complete Alert Routing Logic**
  - **Why**: The current logic is a placeholder. It needs to be able to trigger different actions based on automation rules.
  - **File**: `src/event_handler/main.py`
  - **Action**: In the `route_alert` function, implement the logic to dispatch actions (e.g., call webhooks, send emails) based on the `actions` defined in the matched `AutomationRule` objects.

- [ ] **Data Seeding: Create Initial Data**
  - **Why**: The application needs initial data to function, such as user roles, cameras, and automation rules.
  - **Action**: Create a Django data migration (`./manage.py makemigrations --empty yourapp`) or a custom management command to populate the database with initial `Role`, `User`, `Camera`, and `AutomationRule` objects.

- [ ] **API: Implement Recordings API**
  - **Why**: Users need to be able to view and manage their recordings.
  - **File**: `src/api/recordings.py`
  - **Action**: Implement endpoints to list, search, and download recordings.

# Phase 2: Recording and Playback

- [ ] **Scheduled/Manual Recording**: Implement the logic to trigger recordings based on a schedule or a manual request.
- [ ] **Segment Indexing**: Develop the logic to create and index video segments during the recording process.
- [ ] **Historical Playback Search**: Enhance the recordings API to support searching by camera and time range.
- [ ] **Clip Creation and Export**: Build the functionality to create clips from recordings and export them.
- [ ] **Retention Policies**: Implement a system for automatically deleting old recordings based on retention policies.

---

## 4. Potential Future Work

Items in this section are speculative enhancements — not required for the baseline system to function, but worth considering as the project matures.

### 4.1 MCP (Model Context Protocol) Server

Expose a safety-gated, AI-facing adapter on top of the existing REST API so that LLM clients (Claude Desktop, IDEs, custom agents) can query and — with explicit user confirmation — act on the security system. See `architecture.md` § 6.13.

- [ ] **Scaffold `src/mcp_server/` service**
  - **Why**: Provide a dedicated container that speaks the Model Context Protocol.
  - **Action**: Create a new Python service (`main.py`, `Dockerfile`, `requirements.txt`) using the official `mcp` SDK (`FastMCP`). Add it as an optional profile in `docker-compose.yml`.

- [ ] **Define the initial tool surface (read-only)**
  - **Why**: Ship the lowest-risk capabilities first.
  - **Action**: Implement tools that proxy to the API Gateway: `list_recent_detections`, `get_camera_health`, `search_recordings`, `get_automation_runs`, `summarize_alerts`.

- [ ] **Define MCP resources**
  - **Why**: Allow LLMs to consume structured system context without a tool call per read.
  - **Action**: Expose resources for camera inventory, active automation rules, and the last N hours of detection events.

- [ ] **Define MCP prompt templates**
  - **Why**: Standardize recurring analyst workflows.
  - **Action**: Add templates for "Weekly security audit", "Incident triage for camera X", and "Anomaly summary for the last 24h".

- [ ] **Service account + RBAC scope for MCP**
  - **Why**: Enforce least privilege; the MCP server must not have blanket admin.
  - **Action**: Create a dedicated role `mcp_service` in the auth service with narrowly scoped permissions. Issue an API key/JWT that the MCP server uses when calling the gateway.

- [ ] **Human-in-the-loop confirmation for gated tools**
  - **Why**: Prevent LLM-driven or prompt-injection-driven destructive actions.
  - **Action**: For any tool that mutates state (`request_arm_zone`, `request_create_clip`, PTZ, disarm), return a pending-action token; require a second, user-authenticated confirmation call before dispatching to the gateway.

- [ ] **Audit + observability for MCP invocations**
  - **Why**: Every AI action needs to be traceable.
  - **Action**: Emit an `mcp.tool.invoked` entry into `audit_logs` for every tool call, including the client identity, tool name, arguments hash, and result status. Add Prometheus counters for invocations, denials, and confirmations.

- [ ] **Transport hardening**
  - **Why**: Remote LLM hosts should not reach the MCP server without strong auth.
  - **Action**: Support `stdio` transport for local development and `HTTP + SSE` with OAuth 2.1 for remote use. Restrict remote access to VPN-only in phase 1.

- [ ] **Prompt-injection defense review**
  - **Why**: Detection captions, camera names, and log contents may contain attacker-controlled text.
  - **Action**: Document a policy that treats all data returned from tools/resources as untrusted; ensure gated tools cannot be auto-invoked based solely on content pulled from another tool.

- [ ] **Documentation**
  - **Why**: Onboard future contributors and downstream LLM host operators.
  - **Action**: Add an `MCP.md` (only if explicitly requested later) or a section in the README covering the tool inventory, auth model, and confirmation flow.