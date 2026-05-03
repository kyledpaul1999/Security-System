
import zmq
import os
import json
import time
from datetime import datetime

# --- Django Setup ---
# This must happen before any Django models are imported.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.api.core.settings')
import django
django.setup()
# --- End Django Setup ---

from django.db import transaction
from src.api.detections.models import DetectionEvent
from src.api.automations.models import AutomationRule, AutomationAction
from .actions import send_webhook
from src.api.cameras.models import Camera

def insert_detection_event(event_data):
    """
    Inserts a single detection event into the database using the Django ORM.
    The event data is parsed from the JSON message received from the object detector.
    """
    try:
        camera = Camera.objects.get(id=event_data['camera-id'])
        event_time = datetime.fromtimestamp(event_data['time'])

        DetectionEvent.objects.create(
            camera=camera,
            event_type=event_data['label'],
            confidence=event_data['confidence'],
            frame_ts=event_time,
            metadata={'bounding_box': event_data['bounding_box']}
        )
        print(f"Successfully inserted event for camera {camera.id}")
    except Camera.DoesNotExist:
        print(f"Error: Camera with ID {event_data['camera-id']} not found.")
    except Exception as e:
        print(f"Error inserting detection event: {e}")

def route_alert(event_data):
    """
    Evaluates automation rules against the event and dispatches actions.
    This function first queries the database to find matching rules and then,
    after the transaction is complete, executes the required actions.
    """
    actions_to_run = []

    try:
        # Start a transaction to safely read the rules.
        with transaction.atomic():
            rules = AutomationRule.objects.filter(
                is_active=True, 
                trigger_event_type=event_data['label']
            ).prefetch_related('actions')

            for rule in rules:
                # Simplified condition evaluation for demonstration.
                if event_data['confidence'] > rule.conditions.get('confidence_threshold', 0.85):
                    print(f"Rule 'rule.name' matched!")
                    for action in rule.actions.all():
                        actions_to_run.append({
                            'type': action.action_type,
                            'params': action.action_params,
                        })
    
    except Exception as e:
        print(f"Error reading automation rules: e")
        return # Do not proceed if database read fails

    # --- Execute Actions --- #
    # This part happens *after* the database transaction is closed.
    if not actions_to_run:
        return

    print(f"Executing actions_to_run actions...")
    for action_item in actions_to_run:
        if action_item['type'] == 'send_webhook':
            send_webhook(action_item['params']['url'], event_data)

def main():
    """
    Main function to set up ZeroMQ and start the event processing loop.
    """
    print("Starting Event Handler Service with Django ORM...")

    # Set up ZeroMQ subscriber socket
    zmq_context = zmq.Context()
    sub_socket = zmq_context.socket(zmq.SUB)
    sub_socket.subscribe(b'')
    zmq_sub_url = os.getenv("ZMQ_SUB_URL", "tcp://localhost:5556")
    sub_socket.connect(zmq_sub_url)
    print(f"ZeroMQ subscriber connected to {zmq_sub_url}")

    print("Event handler is ready and waiting for detection events...")
    try:
        while True:
            event_data = sub_socket.recv_json()
            insert_detection_event(event_data)
            route_alert(event_data)

    except KeyboardInterrupt:
        print("Shutting down event handler.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        sub_socket.close()
        zmq_context.term()
        print("Event handler shut down.")

if __name__ == "__main__":
    # Give the database a moment to start up, which is common in containerized environments.
    time.sleep(5)
    main()
