# import tkinter as tk
# from tkinter import ttk

# import requests, json , os, time
# from process import get_running_processes
# from cpu import get_cpu_data
# from installed_software import get_installed_software

# # Replace the URL with the actual URL of your Django API

# check_token_api_url = 'http://127.0.0.1:8000/api/check-token/'
# token_response_file = 'token_response.json'


 
# class NiceApp:
#     def __init__(self, master):
#         self.master = master
#         master.title("Monitoring")
#         master.configure(bg='#ffeead')  # Set background color to white
#         master.geometry("500x500")  # Set the size to 500x500
            
#         if os.path.exists(token_response_file):
#           with open(token_response_file, 'r') as json_file:
#             json_response = json.load(json_file)
#             token = json_response.get('token')
        
#         check_token_api_url_full = check_token_api_url + token
#         check_token_response = requests.get(check_token_api_url_full)

        
#         if check_token_response.status_code == 200:
#             check_token_json_response = check_token_response.json()
#             if check_token_json_response.get('exists'):
#                master.configure(bg="#96ceb4")
#                self.monitoring_label = ttk.Label(master, text="Monitoring Enabled", font=('Helvetica', 18), background='#96ceb4')
#                self.monitoring_label.pack(pady=10)     

#             else:   
#                master.configure(bg="white")
#                error_message = "System not registered / Invalid Authentication Token"
#                self.error_label = ttk.Label(master, text=error_message, font=('Helvetica', 14), background='#ff6f69', foreground='white')
#                self.error_label.pack(pady=10)
        
#         else :
#           master.configure(bg="#ff6f69")  # Change background color to a light red
#           error_message = "Server is not available"
#           self.error_label = ttk.Label(master, text=error_message, font=('Helvetica', 14), background='#ff6f69', foreground='white')
#           self.error_label.pack(pady=10)
          
#         style = ttk.Style()
#         style.configure("TButton",
#                         foreground="white",  # Text color
#                         background="white",  # Button color
#                         font=('Helvetica', 14),
                       
#                         width=50,  # Button width
#                         height=50)  # Button height

#         # Remove button border
#         style.map("TButton",
#                   relief=[('pressed', 'flat'), ('active', 'flat')])

#         self.quit_button = ttk.Button(master, text="Stop", command=master.destroy, style="TButton")
#         self.quit_button.pack(pady=20)

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = NiceApp(root)
#     root.mainloop()





import tkinter as tk
from tkinter import ttk

import requests
import json
import os
import time
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


class NiceApp:
    def __init__(self, master):
        self.master = master
        master.title("Monitoring")
        master.configure(bg='#ffeead')  # Set background color to white
        master.geometry("500x500")  # Set the size to 500x500

        self.update_data()  # Call the function to update data immediately
        self.schedule_update()  # Schedule the function to run periodically

        style = ttk.Style()
        style.configure("TButton",
                        foreground="white",  # Text color
                        background="white",  # Button color
                        font=('Helvetica', 14),
                        width=50,  # Button width
                        height=50)  # Button height

        # Remove button border
        style.map("TButton",
                  relief=[('pressed', 'flat'), ('active', 'flat')])

        self.quit_button = ttk.Button(master, text="Stop", command=master.destroy, style="TButton")
        self.quit_button.pack(pady=20)

    def update_data(self):
        if os.path.exists(token_response_file):
            with open(token_response_file, 'r') as json_file:
                json_response = json.load(json_file)
                token = json_response.get('token')

            
            check_token_response = requests.get(check_token_api_url + token)

            if check_token_response.status_code == 200:
                check_token_json_response = check_token_response.json()
                if check_token_json_response.get('exists'):
                    self.master.configure(bg="#96ceb4")
                    self.monitoring_label = ttk.Label(self.master, text="Monitoring Enabled", font=('Helvetica', 18),
                                                      background='#96ceb4')
                    self.monitoring_label.pack(pady=10)

                    if os.path.exists('cpu_data.json'):
                      print("cpu data sent")
                      with open('cpu_data.json', 'r') as json_file:
                        cpu_data_variable = json.load(json_file)
                        print(cpu_data_variable)

                        # requests.get(send_cpu_data_api(json_file))


                    print("Monitoring logic executed")

                else:
                    self.master.configure(bg="white")
                    error_message = "System not registered / Invalid Authentication Token"
                    self.error_label = ttk.Label(self.master, text=error_message, font=('Helvetica', 14),
                                                 background='#ff6f69', foreground='white')
                    self.error_label.pack(pady=10)

            else:
                self.master.configure(bg="#ff6f69")  # Change background color to a light red
                error_message = "Server is not available"
                self.error_label = ttk.Label(self.master, text=error_message, font=('Helvetica', 14),
                                             background='#ff6f69', foreground='white')
                self.error_label.pack(pady=10)

    def schedule_update(self):
        # Schedule the update_data function to run every 5000 milliseconds (5 seconds)
        self.master.after(5000, self.schedule_update)
        self.update_data()


if __name__ == "__main__":
    root = tk.Tk()
    app = NiceApp(root)
    root.mainloop()
