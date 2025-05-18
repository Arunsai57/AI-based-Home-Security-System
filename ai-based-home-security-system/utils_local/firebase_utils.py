import os
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get values from environment
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH')
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL')

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })


def push_log_to_firebase(name, status, image_path):
    log_ref = db.reference('logs')
    new_log = {
        'name': name,
        'status': status,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'image_path': image_path
    }
    log_ref.push(new_log)
