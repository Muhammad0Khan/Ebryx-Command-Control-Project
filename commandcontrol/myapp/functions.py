from datetime import datetime, timedelta


def get_cpu_12_hours(data):
    timestamps = []
    cpu_usages = []
    
    current_time = datetime.now()
    twelve_hours_ago = current_time - timedelta(hours=18)
    
    for entry in data:
        timestamp_str = entry['data']['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        # print ("bruh why",timestamp_str)
        if timestamp >= twelve_hours_ago:
            # Convert to ISO 8601 format
            iso_timestamp = timestamp.isoformat() + 'Z'
            timestamps.append(iso_timestamp)
            cpu_usages.append(entry['data']['cpu_usage'])
    
    return timestamps, cpu_usages


def process_ram_data(data):
    timestamps = []
    used_swap = []
    free_swap = []
    
    current_time = datetime.now()
    twelve_hours_ago = current_time - timedelta(hours=18)
    
    for entry in data:
        timestamp_str = entry['data']['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        # print ("bruh why",timestamp_str)
        if timestamp >= twelve_hours_ago:
            # Convert to ISO 8601 format
            iso_timestamp = timestamp.isoformat() + 'Z'
            timestamps.append(iso_timestamp)
            used_swap.append(entry['data']['used_swap'])
            free_swap.append(entry['data']['free_swap'])
    
    return timestamps, used_swap,free_swap


def process_disk_data(data):
    timestamps = []
    used_disk = []
    free_disk = []
    
    current_time = datetime.now()
    twelve_hours_ago = current_time - timedelta(hours=18)
    
    for entry in data:
        timestamp_str = entry['data']['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        # print ("bruh why",timestamp_str)
        if timestamp >= twelve_hours_ago:
            # Convert to ISO 8601 format
            iso_timestamp = timestamp.isoformat() + 'Z'
            timestamps.append(iso_timestamp)
            used_disk.append(entry['data']['used_disk'])
            free_disk.append(entry['data']['free_disk'])
    
    return timestamps, used_disk,free_disk

from collections import OrderedDict

def average_cpu_metrics(data_dict):
    total_cpu_count = 0
    total_cpu_usage = 0.0
    total_cpu_frequency = 0.0
    entry_count = 0

    for key, value in data_dict.items():
        for entry in value['data']:
            total_cpu_count += entry['cpu_count']
            total_cpu_usage += entry['data']['cpu_usage']
            total_cpu_frequency += entry['data']['cpu_frequency']
            entry_count += 1

    avg_cpu_count = round(total_cpu_count / entry_count, 2) if entry_count else 0
    avg_cpu_usage = round(total_cpu_usage / entry_count, 2) if entry_count else 0
    avg_cpu_frequency = round(total_cpu_frequency / entry_count, 2) if entry_count else 0

    return avg_cpu_count, avg_cpu_usage, avg_cpu_frequency
    
def average_ram_metrics(data_dict):
    total_ram_size = 0
    total_ram_usage = 0.0
    total_ram_swap = 0.0
    entry_count = 0

    for key, value in data_dict.items():
        for entry in value['data']:
            total_ram_size += entry['total_memory']
            total_ram_usage += entry['data']['percent_memory']
            total_ram_swap += entry['data']['total_swap']
            entry_count += 1

    total_ram_size = round(total_ram_size / entry_count, 2) if entry_count else 0
    total_ram_usage = round(total_ram_usage / entry_count, 2) if entry_count else 0
    total_ram_swap = round(total_ram_swap / entry_count, 2) if entry_count else 0

    return  total_ram_size, total_ram_usage,  total_ram_swap
    
def average_disk_metrics(data_dict):
    total_disk_size = 0
    total_disk_usage = 0.0
    total_percent_disk = 0.0
    entry_count = 0

    for key, value in data_dict.items():
        for entry in value['data']:
            total_disk_size += entry['total_disk']
            total_disk_usage += entry['data']['percent_disk']
            total_percent_disk += entry['data']['used_disk']
            entry_count += 1

    total_disk_size = round(total_disk_size / entry_count, 2) if entry_count else 0
    total_disk_usage = round(total_disk_usage / entry_count, 2) if entry_count else 0
    total_percent_disk = round(total_percent_disk / entry_count, 2) if entry_count else 0

    return  total_disk_size, total_disk_usage,  total_percent_disk
    
