import requests
import json
import os
import time
import signal

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
set_status_online_api = base_url + "/api/set_status_online/"
set_status_offline_api = base_url + "/api/set_status_offline/"
token_response_file = "token_response.json"

client_status = "online"


def notify_server_of_client_status(token, status):
    payload = {"token": token, "status": status}
    response = requests.post(
        set_status_online_api if status == "online" else set_status_offline_api,
        json=payload,
    )
    if response.status_code == 200:
        print(f"Server notified of client status: {status}")
    else:
        print(f"Error notifying server of client status: {status}")


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


def update_client_status_to_online(token):
    notify_server_of_client_status(token, "online")


def update_client_status_to_offline(token):
    notify_server_of_client_status(token, "offline")


def handle_keyboard_interrupt(signal, frame):
    global client_status
    if client_status == "online":
        client_status = "offline"
        update_client_status_to_offline(token)
        print("Client status set to Offline.")
    exit(0)


# Register the signal handler for keyboard interrupt
signal.signal(signal.SIGINT, handle_keyboard_interrupt)

while True:
    if os.path.exists(token_response_file):
        with open(token_response_file, "r") as json_file:
            json_response = json.load(json_file)
            token = json_response.get("token")
            username = json_response.get("username")
    else:
        token = None

    if not token:
        username = input("Enter your username: ")
        if check_username(username):
            generate_token(username)
        else:
            print("Username does not exist. Please create your account.")
            continue

    update_client_status_to_online(token)

    # Add your data sending logic here
    get_cpu_data(token)
    get_installed_software(token)
    save_network_stats(token)

    # Send data to the server
    send_cpu_data(send_cpu_data_api)
    send_installed_software(send_installed_apps_api)
    send_network_stats(send_network_data_api)
    print("Data sent to server.")

    # Sleep for 30 seconds before sending data again
    time.sleep(30)
