import psutil
import csv
import time

def save_cpu_info_to_csv(file_path):
    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        header = [
            'Timestamp',
            'CPU Count',
            'CPU Usage (%)',
            'CPU Frequency (MHz)',
            'Threads'
        ]
        per_cpu_header = ['CPU {} Usage (%)'.format(i) for i in range(psutil.cpu_count())]
        header.extend(per_cpu_header)
        csv_writer.writerow(header)

        try:
            while True:
                # Get CPU information
                cpu_info = psutil.cpu_stats()
                cpu_count = psutil.cpu_count()
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_freq = psutil.cpu_freq()
                threads = psutil.cpu_count(logical=False)

                # Get per-CPU usage
                per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)

                # Get current timestamp
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

                # Create the data row
                data_row = [
                    timestamp,
                    cpu_count,
                    cpu_percent,
                    cpu_freq.current,
                    threads
                ]
                data_row.extend(per_cpu_percent)

                # Write the data row to the CSV file
                csv_writer.writerow(data_row)

                # Wait for 10 seconds
                time.sleep(1)

        except KeyboardInterrupt:
            print("CSV file has been saved.")
            pass

if __name__ == "__main__":
    file_path = "cpu_info.csv"
    save_cpu_info_to_csv(file_path)
