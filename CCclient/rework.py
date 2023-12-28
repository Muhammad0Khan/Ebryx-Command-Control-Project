import requests
import json
import os
import time
from process import *
from cpu import *
from installed_software import *
from network import*

# Replace the URL with the actual URL of your Django API
token_response_file = 'token_response.json'

base_url='http://127.0.0.1:8000'
api_url = base_url+'/api/generate_token'
check_token_api_url = base_url+'/api/check-token/'
send_installed_apps_api = base_url+'/myapp/api/installed_apps/'
send_cpu_data_api = base_url+'/myapp/api/cpu_data/'
send_network_data_api= base_url+'/api/network_data/'


while True:

    if os.path.exists(token_response_file):
        with open(token_response_file, 'r') as json_file:
            json_response = json.load(json_file)
            token = json_response.get('token')

        check_token_response = requests.get(check_token_api_url + token)

        get_cpu_data(token)
        print('cpu data stored')

        get_installed_software(token)
        print('installed data stored')

        save_network_stats(token)
        print ('network stats stored')

        

        if check_token_response.status_code == 200:
            check_token_json_response = check_token_response.json()
            if check_token_json_response.get('exists'):
                # sending data here 
                send_cpu_data(send_cpu_data_api)
                send_network_stats(send_network_data_api)
                # get_installed_software(send_installed_apps_api)

                print("Monitoring logic executed")
            else:
                print("error")

        else:
            print("Server is not available")

    else:
        response = requests.get(api_url)
        if response.status_code == 200:
        
            json_response = response.json()
            token = json_response.get('token')
            print(f'Token (from API): {token}')
            with open(token_response_file, 'w') as json_file:
                json.dump(json_response, json_file, indent=2)
        else:
            print(f'Error: {response.status_code}')
            print(response.text)

    # Sleep for 5 seconds before the next iteration
    time.sleep(5)