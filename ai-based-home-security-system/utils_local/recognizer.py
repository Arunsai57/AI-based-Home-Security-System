import sys
import torch
import cv2
import os
import json
import numpy as np
import sqlite3
from datetime import datetime
import face_recognition

from utils_local.firebase_utils import push_log_to_firebase
from utils_local.email_alert import send_email_alert
from utils_local.sms_alert import send_sms_alert
from ultralytics import YOLO

DB_PATH = 'database/database.db'

# Folder paths
UNKNOWN_SAVE_PATH = 'static/unknown_faces'
KNOWN_SAVE_PATH = 'static/known_logs'
OBJECT_LOG_PATH = 'static/object_logs'
GENERAL_PATH = os.path.join(OBJECT_LOG_PATH, 'general')
WEAPON_PATH = os.path.join(OBJECT_LOG_PATH, 'weapon')
VEHICLE_PATH = os.path.join(OBJECT_LOG_PATH, 'vehicle')
ALERT_PHONE_NUMBER = os.getenv('ALERT_PHONE_NUMBER')

# required folders if not there
for path in [UNKNOWN_SAVE_PATH, KNOWN_SAVE_PATH, GENERAL_PATH, WEAPON_PATH, VEHICLE_PATH]:
    os.makedirs(path, exist_ok=True)

# Cooldown setup
last_alert_time = None
COOLDOWN_SECONDS = 90

# Frame saving control
save_frame_interval = 5
frame_counter = 0

# Surveillance control
surveillance_active = False
video_capture = None

# Load YOLOv8 model
model = YOLO('yolov5s.pt')

# object categories
weapon_labels = ['knife', 'gun', 'scissors']
vehicle_labels = ['car', 'bus', 'truck', 'motorbike', 'bicycle']
general_labels = ['phone', 'bottle', 'laptop', 'remote', 'handbag', 'book', 'cell phone']
latest_frame = None  # browser streaming


def load_known_faces():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, face_encoding FROM persons")
    rows = cursor.fetchall()
    conn.close()

    known_encodings = []
    known_names = []

    for name, encoding_json in rows:
        encoding = np.array(json.loads(encoding_json))
        known_encodings.append(encoding)
        known_names.append(name)

    return known_encodings, known_names


def detect_objects(frame):
    results = model.predict(source=frame, conf=0.5, iou=0.45, imgsz=640, verbose=False)
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append((label, conf, (x1, y1, x2, y2)))
    return detections


def save_object_frame(frame, label):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{ts}.jpg"

    # Determine save path based on object type
    label_lower = label.lower()
    if label_lower in weapon_labels:
        save_path = os.path.join(WEAPON_PATH, filename)
        status = 'WEAPON'
    elif label_lower in vehicle_labels:
        save_path = os.path.join(VEHICLE_PATH, filename)
        status = 'VEHICLE'
    else:
        save_path = os.path.join(GENERAL_PATH, filename)
        status = 'GENERAL'

    cv2.imwrite(save_path, frame)

    # Log to database
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO logs (person_name, status, timestamp, image_path) VALUES (?, ?, ?, ?)",
                 ("Object", status, datetime.now(), filename))
    conn.commit()
    conn.close()

    print(f"[LOGGED] {label} saved as {status} at {filename}")


last_known_face_time = None
UNKNOWN_FACE_COOLDOWN_SECONDS = 10  # cool-down effect ,for now 10


def start_recognition():
    global last_alert_time, frame_counter, surveillance_active, video_capture, latest_frame, last_known_face_time

    known_encodings, known_names = load_known_faces()
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Failed to open camera!")
        surveillance_active = False
        return
    print("[INFO] Surveillance started...")

    while surveillance_active:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to grab frame")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        known_face_detected = False  # Track this per-frame

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            name = "Unknown"
            status = "UNKNOWN"

            if True in matches:
                best_match_index = np.argmin(face_distances)
                name = known_names[best_match_index]
                status = "UNLOCKED"
                known_face_detected = True

            # Saving frame periodically
            if frame_counter % save_frame_interval == 0:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{ts}.jpg" if status == "UNLOCKED" else f"unknown_{ts}.jpg"
                save_path = os.path.join(KNOWN_SAVE_PATH if status == "UNLOCKED" else UNKNOWN_SAVE_PATH, filename)
                cv2.imwrite(save_path, frame)

                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO logs (person_name, status, timestamp, image_path) VALUES (?, ?, ?, ?)",
                             (name, status, datetime.now(), filename))
                image_path = '/' + save_path.replace('\\', '/')
                push_log_to_firebase(name, status, image_path)
                conn.commit()
                conn.close()

            # Drawing boxes
            top, right, bottom, left = face_location
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            color = (0, 255, 0) if status == "UNLOCKED" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Alert logic for unknowns -- with cooldown
        now = datetime.now()
        if known_face_detected:
            last_known_face_time = now
        elif face_encodings:
            time_since_known = (now - last_known_face_time).total_seconds() if last_known_face_time else float('inf')
            if time_since_known > UNKNOWN_FACE_COOLDOWN_SECONDS:
                if not last_alert_time or (now - last_alert_time).total_seconds() > COOLDOWN_SECONDS:
                    send_sms_alert(ALERT_PHONE_NUMBER, '⚠️ Alert: Unknown person detected at the door!')
                    last_alert_time = now

        # Object detection logic
        objects = detect_objects(frame)
        for label, confidence, (x1, y1, x2, y2) in objects:
            label_lower = label.lower()
            if label_lower in weapon_labels + vehicle_labels + general_labels:
                color = (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if frame_counter % save_frame_interval == 0:
                    save_object_frame(frame, label)

                    if label_lower in weapon_labels:
                        if not last_alert_time or (now - last_alert_time).total_seconds() > COOLDOWN_SECONDS:
                            send_sms_alert(ALERT_PHONE_NUMBER, f'🚨 Weapon Detected: {label} spotted on camera!')
                            last_alert_time = now

        frame_counter += 1
        latest_frame = frame.copy()

    if video_capture:
        video_capture.release()
    latest_frame = None
    print("[INFO] Surveillance stopped.")


def stop_recognition():
    global surveillance_active, video_capture
    surveillance_active = False
    if video_capture is not None:
        video_capture.release()
        video_capture = None

        # Force destroy all OpenCV windows
    try:
        cv2.destroyAllWindows()
        for _ in range(5):
            cv2.waitKey(1)  # Process window events for closure
    except Exception as e:
        print(f"[WARN] Error closing OpenCV windows: {e}")