import sqlite3

import face_recognition
import cv2
import time
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, Response ,flash ,session
import os, json
from models import init_db, get_db_connection
from face_utils import encode_face , encode_face_direct
from utils_local import recognizer  # the core function
import threading
from utils_local.firebase_utils import push_log_to_firebase

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
surveillance_thread = None
app.secret_key = 'your_secret_key'

# Initialize DB
init_db()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/manage_persons')
def manage_persons():
    conn = get_db_connection()
    persons = conn.execute("SELECT id, name, image_path FROM persons").fetchall()
    conn.close()
    return render_template('manage_persons.html', persons=persons)


@app.route('/add_person', methods=['POST'])
def add_person():
    name = request.form['name']
    image = request.files['image']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(img_path)

    encoding = encode_face(img_path)
    encoding_json = json.dumps(encoding.tolist())

    conn = get_db_connection()
    conn.execute("INSERT INTO persons (name, image_path, face_encoding) VALUES (?, ?, ?)",
                 (name, img_path, encoding_json))
    conn.commit()
    conn.close()
    return redirect('/manage_persons')


@app.route('/edit_person/<int:id>', methods=['POST'])
def edit_person(id):
    name = request.form['name']
    image = request.files.get('image')

    conn = get_db_connection()

    if image:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(img_path)
        encoding = encode_face(img_path)
        encoding_json = json.dumps(encoding.tolist())
        conn.execute("UPDATE persons SET name=?, image_path=?, face_encoding=? WHERE id=?",
                     (name, img_path, encoding_json, id))
    else:
        conn.execute("UPDATE persons SET name=? WHERE id=?", (name, id))

    conn.commit()
    conn.close()
    return redirect('/manage_persons')


@app.route('/delete_person/<int:id>')
def delete_person(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM persons WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/manage_persons')


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT person_name, status, timestamp, image_path FROM logs WHERE person_name != 'Object' ORDER BY timestamp DESC LIMIT 20")
    logs = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", logs=logs, full=False)


@app.route('/full_history')
def full_history():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT person_name, status, timestamp, image_path FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", logs=logs, full=True)


@app.route('/delete_log', methods=['POST'])
def delete_log():
    timestamp = request.form['timestamp']
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs WHERE timestamp = ?", (timestamp,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


@app.route('/start_surveillance')
def start_surveillance():
    global surveillance_thread

    if not surveillance_thread or not surveillance_thread.is_alive():
        recognizer.surveillance_active = True  # <-- Set the recognizer surveillance active
        surveillance_thread = threading.Thread(target=recognizer.start_recognition)
        surveillance_thread.start()
        print("[INFO] Surveillance thread started.")
    else:
        print("[INFO] Surveillance already running.")

    return redirect(url_for('dashboard'))


@app.route('/stop_surveillance')
def stop_surveillance():
    recognizer.stop_recognition()
    print("[INFO] Surveillance stopping signal sent.")
    return redirect(url_for('dashboard'))


def generate_frames():
    from utils_local import recognizer
    import time
    import numpy as np
    import cv2

    while True:
        if recognizer.latest_frame is None:
            # Create black frame
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Put text on black frame
            cv2.putText(
                black_frame,
                "Surveillance Stopped",
                (80, 240),  # x, y position
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 0, 255),  # red color
                3,
                cv2.LINE_AA
            )
            ret, buffer = cv2.imencode('.jpg', black_frame)
        else:
            ret, buffer = cv2.imencode('.jpg', recognizer.latest_frame)

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.03)  # ~30 FPS

    #
    # # Step 1: Auto-start surveillance if not running
    # # if not recognizer.surveillance_active:
    # #     print("[INFO] Auto-starting Surveillance from Live Feed")
    # #     recognizer.surveillance_active = True
    # #     surveillance_thread = threading.Thread(target=recognizer.start_recognition)
    # #     surveillance_thread.start()
    #
    # #  Instead of opening a new camera, use recognizer's video_capture
    # while True:
    #     if recognizer.video_capture is None:
    #         continue  # Wait until video_capture is ready
    #
    #     success, frame = recognizer.video_capture.read()
    #     if not success:
    #         break
    #     else:
    #         # Encode frame to JPEG
    #         ret, buffer = cv2.imencode('.jpg', frame)
    #         frame = buffer.tobytes()
    #
    #         # Yield frame
    #         yield (b'--frame\r\n'
    #                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/live_feed')
def live_feed():
    return render_template('live_feed.html')


def capture_frame():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Camera not accessible!")

    time.sleep(1.5)  #stabilizing camera

    frames = []
    for _ in range(5):
        ret, frame = cap.read()
        if ret:
            frames.append(frame)

    cap.release()

    if frames:
        return frames[-1]
    else:
        raise Exception("Failed to capture frame!")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            session['message'] = ('success', 'Login Successful!')
            return redirect(url_for('home'))
        else:
            session['message'] = ('error', 'Invalid Credentials!')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/object_logs')
def object_logs():
    conn = get_db_connection()
    logs = conn.execute("SELECT person_name, status, timestamp, image_path FROM logs WHERE person_name = 'Object' ORDER BY timestamp DESC").fetchall()
    conn.close()
    return render_template('object_dashboard.html', logs=logs)


@app.route('/alerts')
def alerts():
    conn = get_db_connection()
    logs = conn.execute("""
        SELECT person_name, status, timestamp, image_path 
        FROM logs 
        WHERE status = 'UNKNOWN' 
           OR status = 'WEAPON'
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return render_template('alerts.html', logs=logs)


if __name__ == '__main__':
    app.run(debug=True)
