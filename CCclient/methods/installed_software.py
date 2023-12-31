import subprocess
import json, requests
from datetime import datetime, timedelta
import os


def get_installed_software(token):
    try:
        # Run system_profiler to get software information
        result = subprocess.run(
            ["system_profiler", "-json", "SPApplicationsDataType"],
            capture_output=True,
            text=True,
        )

        # Parse the JSON output
        software_info = json.loads(result.stdout)

        # Extract the list of installed applications
        applications = software_info.get("SPApplicationsDataType", [])

        # Filter applications modified in the last 5 days
        five_days_ago = datetime.now() - timedelta(days=5)
        modified_applications = [
            update_label(app)
            for app in applications
            if parse_datetime(app.get("lastModified")) >= five_days_ago
        ]

        filename = "modified_installed.json"
        save_data_to_json(token, modified_applications, filename)

        return modified_applications

    except Exception as e:
        print(f"Error: {e}")
        return []


def update_label(application):
    # Update the label "_name" to "name" in the application data
    if "_name" in application:
        application["name"] = application.pop("_name")
    return application


def send_installed_software(api="http://127.0.0.1:8000/myapp/api/installed_apps/"):
    if os.path.exists("modified_installed.json"):
        with open("modified_installed.json", "r") as installed_data_file:
            installed_data = json.load(installed_data_file)
        try:
            response = requests.post(api, json=installed_data)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

            # Optional: Print the response content for debugging
            print(response.content)

            print("installed data successfully sent to the API.")

        except requests.RequestException as e:
            print(f"Error sending installed data to the API: {e}")
    else:
        print("Installed data file (modified_installed.json) not found.")


def parse_datetime(datetime_str):
    # Parse datetime string to a datetime object
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")


def save_data_to_json(token, data, filename):
    # Save the token and data to a JSON file
    with open(filename, "w") as json_file:
        json.dump({"token": token, "data": data}, json_file, indent=2)
        print(f"Token and data saved to {filename}.")


if __name__ == "__main__":
    # Get the list of installed software modified in the last 5 days
    modified_installed_software = get_installed_software()
