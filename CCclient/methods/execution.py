import requests
import subprocess
import json

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = ""

        if result.returncode == 0:
            print(result.stdout)
            output = result.stdout
            return output
        else:
            print(result.stderr)
            output = result.stderr
            return output
    except Exception as e:
        print(f"Error running command: {e}")
        return str(e)

url = "http://127.0.0.1/api/check_issued_commands/"

def fetch_and_save_data(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            for item in data:
                command = item["command"]
                output = run_command(command)

                item["executed"] = True
                item["response"] = output

            with open("issued_commands.json", "w") as file:
                json.dump(data, file, indent=4)
                print("Data saved to issued_commands.json.")
        else:
            print(f"Error fetching data from {url}.")
            print(f"Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data: {e}")


def send_issued_commands(api_url):
    try:
        # Open and read the issued_commands.json file
        with open("issued_commands.json", "r") as json_file:
            commands_data = json.load(json_file)

        # Ensure the data is a list (or appropriate structure)
        if not isinstance(commands_data, list):
            raise ValueError("Invalid data format. Expected a list.")

        print("commands_data", commands_data)
        # Send the data to the specified API URL via a POST request
        response = requests.post(api_url, json=commands_data)

        # Check the response status
        if response.status_code == 200:
            print("Data sent successfully.")
            return response.json()
        else:
            response.raise_for_status()

    except json.JSONDecodeError:
        print("Error: The JSON data could not be decoded.")
    except FileNotFoundError:
        print("Error: The file issued_commands.json was not found.")
    except requests.RequestException as e:
        print(f"Error: An error occurred while sending data to the API. {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
