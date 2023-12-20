# firebase_init.py

from firebase_admin import credentials
import firebase_admin
import os


def initialize_firebase():
    if not firebase_admin._apps:
        # Set the GOOGLE_CLOUD_PROJECT environment variable
        os.environ["GOOGLE_CLOUD_PROJECT"] = "command-and-control-9c601"

        cred = credentials.Certificate(
            "/Users/stormboi/Desktop/project/Ebryx-Command-Control-Project/commandcontrol/firebase/command-and-control-9c601-firebase-adminsdk-zqbso-ec1942a09a.json"
        )
        firebase_config = {
            "apiKey": "AIzaSyCBID8mb8ppM61RFU9pgah5J20VzwOiHbo",
            "authDomain": "command-and-control-9c601.firebaseapp.com",
            "databaseURL": "https://command-and-control-9c601-default-rtdb.firebaseio.com",
            "storageBucket": "command-and-control-9c601.appspot.com",
            "messagingSenderId": "595205364194",
            "appId": "1:595205364194:web:7d77ff7d256f2526db81bb",
        }

        firebase_admin.initialize_app(cred, options=firebase_config)
        print("Firebase app initialized successfully.")
    else:
        print("Firebase app already initialized")
