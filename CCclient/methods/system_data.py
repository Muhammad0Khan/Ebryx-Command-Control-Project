import platform, psutil
import socket
import json
import os, requests

def save_system_information(token): 
  try:
    operating_system = platform.system()
    hostname = socket.gethostname()
    username = psutil.users()[0].name
    operating_system_version = platform.mac_ver()[0]

    if (operating_system=="Darwin"):
      operating_system="MacOS"

    system_data={
      "token": token,
      "username" : username, 
      "hostname" : hostname, 
      "operating_system" : operating_system, 
      "operating_system_version" : operating_system_version, 
    }

    with open("system_data.json", "w") as json_file:
              json.dump(system_data, json_file, indent=2)
  except KeyboardInterrupt:
          print("Data has been saved to cpu_info.json.")


def send_system_data(api="http://127.0.0.1:8000/myapp/api/system_data/"):
    if os.path.exists("system_data.json"):
        with open("system_data.json", "r") as system_data_file:
            system_data = json.load(system_data_file)

            # Assuming `api` is the endpoint URL where you want to send the JSON data
            try:
                response = requests.post(api, json=system_data)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

                # Optional: Print the response content for debugging
                print(response.content)

                print("System data successfully sent to the API.")
            except requests.RequestException as e:
                print(f"Error sending System data to the API: {e}")
    else:
        print("System data file (system_data.json) not found.")