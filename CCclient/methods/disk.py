import psutil
import time
import json
import os
import requests
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def send_disk_data(api="http://127.0.0.1:8000/api/disk_data/"):
    """Send disk data to the specified API endpoint."""
    disk_data_file = "disk_data.json"

    if os.path.exists(disk_data_file):
        try:
            with open(disk_data_file, "r") as file:
                disk_data = json.load(file)

            response = requests.post(api, json=disk_data)
            response.raise_for_status()
            logging.info("Disk data successfully sent to the API.")
            logging.debug(f"API Response: {response.content}")
        except requests.RequestException as e:
            logging.error(f"Error sending disk data to the API: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Error reading JSON data: {e}")
    else:
        logging.warning(f"Disk data file ({disk_data_file}) not found.")


def bytes_to_megabytes(bytes):
    """Convert bytes to megabytes and round to one decimal place."""
    return round(bytes / (1024 * 1024), 1)


def save_disk_data(token):
    """Gather disk data using psutil and save it to a JSON file."""

    def bytes_to_megabytes(bytes_value):
        """Convert bytes to megabytes."""
        return bytes_value / (1024**2)

    try:
        disk_usage = psutil.disk_usage("/")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        disk_data = {
            "total_disk": bytes_to_megabytes(disk_usage.total),
            "data": {
                "timestamp": timestamp,
                "used_disk": bytes_to_megabytes(disk_usage.used),
                "free_disk": bytes_to_megabytes(disk_usage.free),
                "percent_disk": round(disk_usage.percent, 1),
            },
        }
        disk_data["token"] = token

        try:
            with open("disk_data.json", "w") as file:
                json.dump(disk_data, file, indent=2)
            logging.info("Disk data successfully saved to disk_data.json.")
        except IOError as e:
            logging.error(f"Error writing to JSON file: {e}")
    except Exception as e:
        logging.error(f"Error gathering disk data: {e}")
