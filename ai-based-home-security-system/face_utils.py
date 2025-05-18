import face_recognition
import numpy as np


def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        return encodings[0]
    else:
        raise Exception("No face found in the image!")


def encode_face_direct(frame):
    rgb_frame = frame[:, :, ::-1]  # BGR to RGB

    # Step 1: Find faces
    face_locations = face_recognition.face_locations(rgb_frame)

    # Step 2: If no face detected, exit safely
    if not face_locations:
        print("No face detected in frame!")
        return None

    # Step 3: Try encoding
    try:
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not encodings:
            print("Face found but unable to encode!")
            return None

        return encodings[0]

    except Exception as e:
        print(f"Exception during encoding: {e}")
        return None