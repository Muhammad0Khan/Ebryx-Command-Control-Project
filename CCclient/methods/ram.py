import psutil
import time
import json
import os
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def send_ram_data(api="http://127.0.0.1:8000/myapp/api/ram_data/"):
    """Send RAM data to the specified API endpoint."""
    ram_data_file = "ram_data.json"
    
    if os.path.exists(ram_data_file):
        try:
            with open(ram_data_file, "r") as file:
                ram_data = json.load(file)
                
            response = requests.post(api, json=ram_data)
            response.raise_for_status()
            logging.info("RAM data successfully sent to the API.")
            logging.debug(f"API Response: {response.content}")
        except requests.RequestException as e:
            logging.error(f"Error sending RAM data to the API: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Error reading JSON data: {e}")
    else:
        logging.warning(f"RAM data file ({ram_data_file}) not found.")

def bytes_to_megabytes(bytes):
    """Convert bytes to megabytes."""
    return bytes / (1024 * 1024)

def save_ram_data(token):
    """Gather RAM data using psutil and save it to a JSON file."""
    def bytes_to_megabytes(bytes_value):
        """Convert bytes to megabytes."""
        return bytes_value / (1024 ** 2)
    
    try:
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        ram_data = {
            "total_memory": round(bytes_to_megabytes(virtual_memory.total), 2),
            "data": {
                "timestamp": timestamp,
                "available_memory": round(bytes_to_megabytes(virtual_memory.available), 2),
                "used_memory": round(bytes_to_megabytes(virtual_memory.used), 2),
                "free_memory": round(bytes_to_megabytes(virtual_memory.free), 2),
                "percent_memory": round(virtual_memory.percent, 2),
                "total_swap": round(bytes_to_megabytes(swap_memory.total), 2),
                "used_swap": round(bytes_to_megabytes(swap_memory.used), 2),
                "free_swap": round(bytes_to_megabytes(swap_memory.free), 2),
                "percent_swap": round(swap_memory.percent, 2),
            },
        }
        ram_data["token"] = token

        try:
            with open("ram_data.json", "w") as file:
                json.dump(ram_data, file, indent=2)
            logging.info("RAM data successfully saved to ram_data.json.")
        except IOError as e:
            logging.error(f"Error writing to JSON file: {e}")
    except Exception as e:
        logging.error(f"Error gathering RAM data: {e}")


