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

