import subprocess
import psutil
from datetime import datetime, timedelta

def get_installed_apps_last_12_hours():
    # Calculate the time 12 hours ago from now
    twelve_hours_ago = datetime.now() - timedelta(hours=12)

    # Format the time in the required format for journalctl
    time_filter = twelve_hours_ago.strftime("%Y-%m-%dT%H:%M:%S")

    # Run the journalctl command to get installed applications in the last 12 hours
    command = f"journalctl --since '{time_filter}' | grep 'Installed package' | awk '{{print $NF}}'"

    try:
        result = subprocess.check_output(command, shell=True, text=True)
        installed_apps = result.splitlines()
        return installed_apps
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    installed_apps_last_12_hours = get_installed_apps_last_12_hours()

    if installed_apps_last_12_hours:
        print("Installed applications in the last 12 hours:")
        for app in installed_apps_last_12_hours:
            print(app)
    else:
        print("No applications installed in the last 12 hours.")

def get_running_processes():
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
    processes.sort(key=lambda x: x['memory_percent'] if x['memory_percent'] is not None else float('-inf'), reverse=True)
    return processes

if __name__ == "__main__":
    running_processes = get_running_processes()

    if running_processes:
        print("Currently running processes:")
        for process in running_processes:
            print(f"PID: {process['pid']}, Name: {process['name']}, Username: {process['username']}")
    else:
        print("No processes are currently running.")