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

def gather_ram_data():
    """Gather RAM data using psutil."""
    try:
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        ram_data = {
            "data": {
                "timestamp": timestamp,
                "total_memory": bytes_to_megabytes(virtual_memory.total),
                "available_memory": bytes_to_megabytes(virtual_memory.available),
                "used_memory": bytes_to_megabytes(virtual_memory.used),
                "free_memory": bytes_to_megabytes(virtual_memory.free),
                "percent_memory": virtual_memory.percent,
                "total_swap": bytes_to_megabytes(swap_memory.total),
                "used_swap": bytes_to_megabytes(swap_memory.used),
                "free_swap": bytes_to_megabytes(swap_memory.free),
                "percent_swap": swap_memory.percent,
            },
        }
        return ram_data
    except Exception as e:
        logging.error(f"Error gathering RAM data: {e}")
        return None

def save_ram_data(ram_data, token):
    """Save gathered RAM data to a JSON file."""
    if ram_data:
        ram_data["token"] = token
        try:
            with open("ram_data.json", "w") as file:
                json.dump(ram_data, file, indent=2)
            logging.info("RAM data successfully saved to ram_data.json.")
        except IOError as e:
            logging.error(f"Error writing to JSON file: {e}")

def main(token, api_url):
    ram_data = gather_ram_data()
    save_ram_data(ram_data, token)
    # send_ram_data(api_url)

if __name__ == "__main__":
    TOKEN = "your_token_here"
    API_URL = "http://127.0.0.1:8000/myapp/api/ram_data/"
    main(TOKEN, API_URL)
