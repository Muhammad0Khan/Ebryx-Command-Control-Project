import psutil
from datetime import datetime
import json


def get_running_processes(token):
    processes = []

    for process in psutil.process_iter(['pid', 'name', 'username', 'create_time', 'cpu_percent', 'memory_percent']):
        create_time = datetime.fromtimestamp(process.info['create_time'])
        running_time = datetime.now() - create_time
        running_time_str = str(running_time).split(".")[0]  # Format running time as string

        cpu_percent = process.info.get('cpu_percent', None)
        memory_percent = process.info.get('memory_percent', None)

        processes.append({
            'pid': process.info['pid'],
            'name': process.info['name'],
            'username': process.info['username'],
            'running_time': running_time_str,
            'cpu_percent': round(cpu_percent, 2) if cpu_percent is not None else None,
            'memory_percent': round(memory_percent, 2) if memory_percent is not None else None,
        })

    # Sort processes by CPU percent (high to low), treating None as lowest priority
    data = {'token': token, 'processes': processes}

    with open('processes_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)
        
    return data

if __name__ == "__main__":
    # If the script is run directly, call the function and print the result
    result = get_running_processes()
    print(result)