
import zmq
import psycopg2
from psycopg2 import OperationalError
import os
import json
import time
from datetime import datetime

# This service subscribes to detection events, saves them to the TimescaleDB database,
# and includes a placeholder for future alert routing logic. It acts as the final sink
# for the data pipeline.

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Retries several times if the database is not ready, which is useful in
    a containerized startup sequence.
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
    print("Could not establish database connection. Exiting.")
    return None

def insert_detection_event(conn, event_data):
    """
    Inserts a single detection event into the TimescaleDB database.
    The event data is parsed from the JSON message received from the object detector.
    """
    sql = """INSERT INTO detection_events (time, camera_id, label, confidence, bounding_box)
             VALUES (%s, %s, %s, %s, %s);"""
    try:
        with conn.cursor() as cur:
            # Convert Unix timestamp to a timezone-aware datetime object
            event_time = datetime.fromtimestamp(event_data['time'])
            # The bounding_box is converted to a JSON string for the JSONB column
            bounding_box_json = json.dumps(event_data['bounding_box'])
            
            cur.execute(sql, (
                event_time,
                event_data['camera_id'],
                event_data['label'],
                event_data['confidence'],
                bounding_box_json
            ))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error inserting detection event: {e}")
        conn.rollback() # Roll back the transaction on error

def route_alert(event_data):
    """
    Placeholder function for routing alerts.
    In a real system, this function would trigger notifications (e.g., email, SMS, push notification)
    based on the nature of the detection event (e.g., detecting a 'person' in a restricted area).
    """
    # Example: Send an alert if a person is detected with high confidence
    if event_data['label'] == 'person' and event_data['confidence'] > 0.85:
        print(f"ALERT: Person detected on camera {event_data['camera_id']} with {event_data['confidence']:.2f} confidence.")
        # Here you would add code to send an email, SMS, or other notification.

def main():
    """
    Main function to set up ZeroMQ, connect to the database, and start the event processing loop.
    """
    print("Starting Event Handler Service...")

    # Connect to the database
    db_conn = get_db_connection()
    if not db_conn:
        return

    # Set up ZeroMQ subscriber socket
    # This socket listens for detection events published by the object_detector service.
    zmq_context = zmq.Context()
    sub_socket = zmq_context.socket(zmq.SUB)
    sub_socket.subscribe(b'')  # Subscribe to all messages
    zmq_sub_url = os.getenv("ZMQ_SUB_URL", "tcp://localhost:5556")
    sub_socket.connect(zmq_sub_url)
    print(f"ZeroMQ subscriber connected to {zmq_sub_url}")

    print("Event handler is ready and waiting for detection events...")
    try:
        while True:
            # Receive a JSON-formatted detection event
            event_data = sub_socket.recv_json()
            
            # Insert the event into the database
            insert_detection_event(db_conn, event_data)
            
            # Process the event for potential alerts
            route_alert(event_data)

    except KeyboardInterrupt:
        print("Shutting down event handler.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up database and ZeroMQ resources
        if db_conn:
            db_conn.close()
        sub_socket.close()
        zmq_context.term()
        print("Event handler shut down.")

if __name__ == "__main__":
    main()
