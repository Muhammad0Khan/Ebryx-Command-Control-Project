from datetime import datetime, timedelta


def get_cpu_12_hours(data):
    timestamps = []
    cpu_usages = []
    
    current_time = datetime.now()
    twelve_hours_ago = current_time - timedelta(hours=12)
    
    for entry in data:
        timestamp_str = entry['data']['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        if timestamp >= twelve_hours_ago:
            # Convert to ISO 8601 format
            iso_timestamp = timestamp.isoformat() + 'Z'
            timestamps.append(iso_timestamp)
            cpu_usages.append(entry['data']['cpu_usage'])
    
    return timestamps, cpu_usages
