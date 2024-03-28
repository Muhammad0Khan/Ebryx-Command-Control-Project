import requests
import json
import os
import time
import hashlib

from methods.process import *
from methods.cpu import *
from methods.installed_software import *
from methods.network import *

base_url = "http://127.0.0.1:8000"
check_username_api_url = base_url + "/api/check_username/"
check_token_api_url = base_url + "/api/check_token/"
send_installed_apps_api = base_url + "/api/installed_apps/"
send_cpu_data_api = base_url + "/api/cpu_data/"
send_network_data_api = base_url + "/api/network_data/"
set_status_offline_api = base_url + "/api/set_status_offline/"
token_response_file = "token_response.json"


def notify_server_of_offline_status(token):
    payload = {"token": token}
    print(f"Token: {token}")
    response = requests.post(set_status_offline_api, json=payload)
    if response.status_code == 200:
        print("Server notified of offline status")
    else:
        print("Error notifying server of offline status")


def check_username(username):
    response = requests.get(check_username_api_url + username)
    if response.status_code == 200:
        json_response = response.json()
        return json_response.get("exists")
    return False


def generate_token(username):
    token = input("Enter your token: ")
    with open(token_response_file, "w") as json_file:
        json.dump({"token": token, "username": username}, json_file, indent=2)
    print("Token Saved.")


while True:
    if os.path.exists(token_response_file):
        with open(token_response_file, "r") as json_file:
            json_response = json.load(json_file)
            token = json_response.get("token")
        print("Token: ", token)
    else:
        token = None

    if not token:
        username = input("Enter your username: ")
        if check_username(username):
            generate_token(username)
        else:
            print("Username does not exist. Please create your account.")
            continue

    if token:
        check_token_response = requests.get(check_token_api_url + token)
        get_cpu_data(token)
        get_installed_software(token)
        save_network_stats(token)

        if check_token_response.status_code == 200:
            check_token_json_response = check_token_response.json()
            if check_token_json_response.get("exists"):
                send_cpu_data(send_cpu_data_api)
                send_installed_software(send_installed_apps_api)
                send_network_stats(send_network_data_api)

                print("Data sent to server.")
            else:
                print("Token does not exist.")
        else:
            print("Error checking token.")
    else:
        print("Token not found.")

    notify_server_of_offline_status(token)

    time.sleep(30)
