import psutil
import time
import os
import pandas as pd
import json
import random
import string
import requests


def generate_token(length=24):
    """
    Generates a random token with the specified length.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def save_network_stats(token):
    # get the network I/O stats from psutil on each network interface
    # by setting `pernic` to `True`
    io = psutil.net_io_counters(pernic=True)

        # sleep for `UPDATE_DELAY` seconds
       
        # get the network I/O stats again per interface 
    io_2 = psutil.net_io_counters(pernic=True)
        # initialize the data to gather (a list of dicts)
    data = {"token": token, "data": []}
    for iface, iface_io in io.items():
            # new - old stats gets us the speed
            upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, io_2[iface].bytes_recv - iface_io.bytes_recv
            data["data"].append({
                {"iface": iface,
                 data:{
                     "download": get_size(io_2[iface].bytes_recv),
                "total_upload": get_size(io_2[iface].bytes_sent),
                "upload_speed": f"{get_size(upload_speed / 1)}",
                "download_speed": f"{get_size(download_speed / 1)}",
                     
                 }}
                
            })
        # update the I/O stats for the next iteration
    io = io_2
        # construct a Pandas DataFrame to print stats in a cool tabular style
    df = pd.DataFrame(data["data"])

        # sort values per column, feel free to change the column
    df.sort_values("Download", inplace=True, ascending=False)
        
        
    with open('network_stats.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)
        
    print("JSON saved to:", "network_stats.json")

def send_network_stats (api): 
    if os.path.exists('network_stats.json'):
        with open('network_stats.json', 'r') as network_data_file:
            cpu_data = json.load(network_data_file)

            try:
                response = requests.post(api, json=cpu_data)
                response.raise_for_status()  
                print(response.content)

                print("network data successfully sent to the API.")
            except requests.RequestException as e:
                print(f"Error sending network data to the API: {e}")
    else:
        print("network data file (network_stats.json) not found.")