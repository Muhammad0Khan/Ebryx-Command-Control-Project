import psutil
import time
import json
import os
import requests
import platform
import socket


def send_cpu_data(api="http://127.0.0.1:8000/myapp/api/cpu_data/"):
    if os.path.exists('cpu_data.json'):
        with open('cpu_data.json', 'r') as cpu_data_file:
            cpu_data = json.load(cpu_data_file)

            # Assuming `api` is the endpoint URL where you want to send the JSON data
            try:
                response = requests.post(api, json=cpu_data)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

                # Optional: Print the response content for debugging
                print(response.content)

                print("CPU data successfully sent to the API.")
            except requests.RequestException as e:
                print(f"Error sending CPU data to the API: {e}")
    else:
        print("CPU data file (cpu_data.json) not found.")
        




def get_cpu_data(token):
    try:
        # Get CPU Information
        cpu_info = psutil.cpu_stats()
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=None)
        system_name = platform.system()
        hostname = socket.gethostname()


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

        # Save CPU Information to a JSON file
        cpu_data = {
            "token": token,
            "cpu_count": cpu_count,
            "threads": threads,
            "system_name": system_name,
            "hostname": hostname,
            "data": {
                "timestamp": timestamp,
                "cpu_usage": cpu_percent,
                "cpu_frequency": cpu_freq_value,
                "per_cpu_percent": per_cpu_percent,
            }
        }
        with open('cpu_data.json', 'w') as json_file:
            json.dump(cpu_data, json_file, indent=2)

    except KeyboardInterrupt:
        print("Data has been saved to cpu_info.json.")

if __name__ == "__main__":
    get_cpu_data()
