import requests, json , os, time
from process import *
from cpu import *
from installed_software import *

# Replace the URL with the actual URL of your Django API
token_response_file = 'token_response.json'

base_url='http://127.0.0.1:8000/'
api_url = base_url+'/api/generate_token'
check_token_api_url = base_url+'/api/check-token/'
send_installed_apps_api = base_url+'/myapp/api/installed_apps/'
send_cpu_data_api = base_url+'/myapp/api/cpu_data/'



while True:
    if os.path.exists(token_response_file):
        with open(token_response_file, 'r') as json_file:
            json_response = json.load(json_file)
            token = json_response.get('token')
        
        check_token_response = requests.get(check_token_api_url + token)

        
        if check_token_response.status_code == 200:
            check_token_json_response = check_token_response.json()
            if check_token_json_response.get('exists'):
                    
                    # functions storing the data, with token ID
                    processes_result = get_running_processes(token)
                    cpu_result = get_cpu_data(token)
                    send_cpu_data(send_cpu_data_api)

                    print('It works!')
                    
            else:
                    print('Token does not exist.')
        else:
            print(f'Error checking token: {check_token_response.status_code}')
            print(check_token_response.text)

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

    # Sleep for 30 seconds before the next iteration
    time.sleep(5)