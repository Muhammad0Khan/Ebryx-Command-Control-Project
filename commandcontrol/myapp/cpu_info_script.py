import os
import sys
import time
import psutil
import requests  # Added requests library for HTTP requests

# Set the path to your Firebase Admin SDK credentials JSON file
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/Users/admin/Desktop/Ebryx/commandcontrol/firebase/command-and-control-9c601-firebase-adminsdk-zqbso-ec1942a09a.json"

# Add the Django project path to the sys.path
sys.path.append("/commandcontrol/")

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "commandcontrol.settings")

import django

django.setup()

from firebase_admin import initialize_app, db
from myapp.models import CPUInfo
from commandcontrol.celery import app

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyCBID8mb8ppM61RFU9pgah5J20VzwOiHbo",
    "authDomain": "command-and-control-9c601.firebaseapp.com",
    "databaseURL": "https://command-and-control-9c601-default-rtdb.firebaseio.com",
    "projectId": "command-and-control-9c601",
    "storageBucket": "command-and-control-9c601.appspot.com",
    "messagingSenderId": "595205364194",
    "appId": "1:595205364194:web:7d77ff7d256f2526db81bb",
}

# Initialize Firebase
initialize_app(options=firebase_config)

# Set the URL of your Django server's endpoint for saving CPU information
server_url = "https://52a9-103-145-185-153.ngrok-free.app/remote_cpu_info_api/"


@app.task
def save_cpu_info_to_firebase_and_server():
    try:
        while True:
            # Get CPU Information
            cpu_info = psutil.cpu_stats()
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=None)

            try:
                cpu_freq = psutil.cpu_freq()
                cpu_freq_value = cpu_freq.current
            except FileNotFoundError:
                cpu_freq_value = -1

            threads = psutil.cpu_count(logical=False)

            # Get per-CPU Usage
            per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)

            # Get current Timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # Save CPU Information to Firebase
            firebase_ref = db.reference("profile_cpu_info")
            firebase_ref.push(
                {
                    "Timestamp": timestamp,
                    "CPU Count": cpu_count,
                    "CPU Usage (%)": cpu_percent,
                    "CPU Frequency (MHz)": cpu_freq_value,
                    "Threads": threads,
                    "Per CPU Usage (%)": per_cpu_percent,
                }
            )

            # Save CPU Information to Django Model via HTTP POST request
            payload = {
                "username": "testing123",
                "timestamp": timestamp,
                "cpu_count": cpu_count,
                "cpu_percent": cpu_percent,
                "cpu_freq_value": cpu_freq_value,
                "threads": threads,
                "per_cpu_percent": per_cpu_percent,
            }
            response = requests.post(server_url, json=payload)

            if response.status_code == 200:
                print("CPU information sent successfully.")
            else:
                print(
                    f"Failed to send CPU information. Status code: {response.status_code}"
                )

            time.sleep(5)

    except KeyboardInterrupt:
        print("Data has been saved to Firebase and Django.")


if __name__ == "__main__":
    save_cpu_info_to_firebase_and_server()
