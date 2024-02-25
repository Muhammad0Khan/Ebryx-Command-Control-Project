# firebase_init.py

from firebase_admin import initialize_app
import os


def initialize_firebase():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
        "/Users/stormboi/Downloads/University/project/Ebryx-Command-Control-Project/commandcontrol/firebase/command-and-control-9c601-firebase-adminsdk-zqbso-ec1942a09a.json"
    )

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
