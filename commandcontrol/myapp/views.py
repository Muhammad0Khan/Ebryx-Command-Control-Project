import datetime
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from myapp.models import *

import json, time
from firebase_admin import db
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from .models import *
from django.shortcuts import render, redirect
from .serializers import InstalledAppSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import SignupForm, LoginForm
from django.views.decorators.http import require_POST
import pyrebase
from .firebase_init import initialize_firebase
from django.urls import reverse
from functools import wraps
from myapp.methods import *
from .functions import *


from django.shortcuts import render
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO

try:
    firebase_admin = initialize_firebase()
except ValueError:
    pass

config = {
    "apiKey": "AIzaSyCBID8mb8ppM61RFU9pgah5J20VzwOiHbo",
    "authDomain": "command-and-control-9c601.firebaseapp.com",
    "databaseURL": "https://command-and-control-9c601-default-rtdb.firebaseio.com",
    "storageBucket": "command-and-control-9c601.appspot.com",
    "messagingSenderId": "595205364194",
    "appId": "1:595205364194:web:7d77ff7d256f2526db81bb",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database = firebase.database()


# @login_required
def logout_view(request):
    if "firebase_user_id_token" in request.session:
        del request.session["firebase_user_id_token"]

    return redirect("login")


# added apis here
@api_view(["GET"])
def generate_token(request):
    # Generate a unique token
    token = get_random_string(length=40)
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Store the token in Firestore
    ref = db.reference("tokens")
    ref.push().set({"token": token, "generation_timestamp" : timestamp })

    ref_create_online_status = db.reference("status")
    ref_create_online_status.push().set({"token": token, "status": "offline"})

    message = "new system added"
    type = "New System"
    set_notification(message, type)
    # Return the token in the API response
    return Response({"token": token})



def check_token(request, token):
    try:
        # Reference to the Firebase Realtime Database node where you store tokens
        tokens_ref = db.reference("/tokens")

        # Query the database to check if the token exists
        query = tokens_ref.order_by_child("token").equal_to(token).get()
        update_token_status(token)
        set_status_offline(token, delay=30)

        if query:
            return JsonResponse({"exists": True})
        else:
            return JsonResponse({"exists": False})
    except Exception as e:
        return JsonResponse({"error": str(e)})


@csrf_exempt
def save_firebase_token(token_value):
    APIToken.objects.create(token_value=token_value)


class InstalledAppAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InstalledAppSerializer(data=request.data)
        if serializer.is_valid():
            # Save to the Firebase Realtime Database
            token = serializer.validated_data.get("token")
            firebase_ref = db.reference(f"/installed_apps/{token}")
            firebase_ref.set(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                # Create a new user in Firebase Authentication
                user = auth.create_user_with_email_and_password(email, password)

                # Store additional user data in the Firebase Realtime Database
                user_data = {"email": email}
                database.child("users").child(user["localId"]).set(user_data)

                # Redirect to login after successful signup

                return redirect("login")
            except Exception as e:
                # Handle signup failure
                print(f"Error in signup_view: {e}")
                # You might want to add an error message here

    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})


def firebase_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("firebase_user_id_token"):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                # Authenticate user against Firebase Authentication
                user = auth.sign_in_with_email_and_password(email, password)

                # Store Firebase User ID token in the session
                request.session["firebase_user_id_token"] = user["idToken"]

                # Authenticate Django user (optional, only if you need to use Django authentication)
                # django_user = authenticate(request, email=email, password=password)

                # Redirect to the dashboard or any other page upon successful login
                next_url = request.GET.get("next", None)

                # If next_url is not specified, redirect to the default dashboard view
                if not next_url:
                    next_url = reverse("dashboard")

                return redirect(next_url)
            except Exception as e:
                # Handle login failure
                print(f"Error in login_view: {e}")
                # You might want to add an error message here

    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


@firebase_auth_required
def dashboard_view(request):
    tokens_ref = db.reference("tokens")
    status_ref = db.reference("status")
    system_ref = db.reference("system_data")
    notifications_ref= db.reference("notifications")
    
    tokens_data = tokens_ref.order_by_child("token").get()
    status_data = status_ref.order_by_child("token").get()
    system_data = system_ref.order_by_child("token").get()
    notifications_data= notifications_ref.get()

    tokens = []
    systems_online = 0

    for token_key, token in tokens_data.items():
        # Check if there is a corresponding status for the token
        status_key = next(
            (
                key
                for key, value in status_data.items()
                if value["token"] == token["token"]
            ),
            None,
        )
        status = status_data.get(status_key, {}) if status_key else {}
        if status.get('status') == 'online':
            systems_online += 1

        # Check if there is system data for the token
        system_details = system_data.get(token["token"], {})  # Fetch system details based on token

        # Create a dictionary with token details, status, and system data
        token_details = {
            "token": token["token"],
            "details_url": f'/token-details/{token["token"]}/',
            "hardware_info": f'/api/hardware_info/{token["token"]}/',
            "status": status.get("status", "N/A"),  # Use 'N/A' if no status found
            "system_data": system_details  # Include system data
        }

        tokens.append(token_details)
    print (notifications_data)
    dashboard_data = {
        "tokens": tokens,
        "online_count": systems_online,
        "notifications": notifications_data, 
    }
    return render(request, "dashboard.html", dashboard_data)

@firebase_auth_required
def hardware_dashboard_view(request):
    tokens_ref = db.reference("tokens")
    status_ref = db.reference("status")
    cpu_data_ref = db.reference("cpu_data")
    ram_data_ref = db.reference("ram_data")
    disk_data_ref = db.reference("disk_data")
    system_ref = db.reference("system_data")

    system_data = system_ref.order_by_child("token").get()
    tokens_data = tokens_ref.order_by_child("token").get()
    status_data = status_ref.order_by_child("token").get()
    cpu_data = cpu_data_ref.order_by_child("token").get()
    ram_data = ram_data_ref.order_by_child("token").get()
    disk_data = disk_data_ref.order_by_child("token").get()

    avg_count, avg_usage, avg_freq = average_cpu_metrics(cpu_data)
    ram_avg_size, ram_avg_usage,  ram_avg_swap= average_ram_metrics(ram_data)
    total_disk_size, total_disk_usage,  total_percent_disk = average_disk_metrics(disk_data)
    print ("___")
    print ("looking at",  total_disk_size, total_disk_usage,  total_percent_disk)

    tokens = []
    for token_key, token in tokens_data.items():
        status_key = next(
            (
                key
                for key, value in status_data.items()
                if value["token"] == token["token"]
            ),
            None,
        )
        status = status_data.get(status_key, {}) if status_key else {}
        system_details = system_data.get(token["token"], {})  # Fetch system details based on token

        token_details = {
            "token": token["token"],
            "hardware_info": f'/api/hardware_info/{token["token"]}/',
            "status": status.get("status", "N/A"),
            "system_data": system_details  # Include system data

        }
        
        tokens.append(token_details)
        data={
            "tokens": tokens,
             # cpu avgs
            "avg_count":avg_count, 
            "avg_usage":avg_usage,
            "avg_freq": avg_freq, 

            # ram avgs 
            "ram_avg_size":ram_avg_size, 
            "ram_avg_usage" : ram_avg_usage,  
            "ram_avg_swap":ram_avg_swap, 

            # disk avgs
            "total_disk_size" :total_disk_size,
            "total_disk_usage": total_disk_usage,  
            "total_percent_disk": total_percent_disk, 
        }

    return render(request, "hardware_dashboard.html", data)


def token_details_view(request, token):
    # Fetch data from the installed_apps collection for the specific token
    apps_ref = db.reference("installed_apps").child(token)
    system_data_ref = db.reference("system_data").child(token)
    system_data = system_data_ref.get()
    token_data = apps_ref.get()

    if token_data:
        installed_apps_data = token_data.get("data", [])
    else:
        installed_apps_data = []

    # Get filter parameters from the request
    name_filter = request.GET.get('name', '')
    version_filter = request.GET.get('version', '')
    last_modified_filter = request.GET.get('last_modified', '')

    # Filter installed apps data
    if name_filter:
        installed_apps_data = [app for app in installed_apps_data if name_filter.lower() in app.get('name', '').lower()]

    if version_filter:
        installed_apps_data = [app for app in installed_apps_data if version_filter in app.get('version', '')]

    if last_modified_filter:
        try:
            last_modified_date = datetime.strptime(last_modified_filter, '%Y-%m-%d')
            installed_apps_data = [
                app for app in installed_apps_data
                if datetime.strptime(app.get('lastModified', ''), '%Y-%m-%dT%H:%M:%SZ').date() == last_modified_date.date()
            ]
        except ValueError:
            # Handle the case where the date is not in the correct format
            pass

    return render(
        request,
        "token_details.html",
        {
            "system_data": system_data,
            "installed_apps": installed_apps_data,
            "request": request,  # Pass the request object to access GET parameters in the template
        },
    )

def update_token_status(token):
    print("function called ")
    # Reference to the 'status' collection
    status_ref = db.reference("status")

    # Find the status entry for the given token
    status_data = status_ref.order_by_child("token").equal_to(token).get()

    print(status_data)

    # Update the status to 'online' if a matching status is found
    if status_data:
        status_key = list(status_data.keys())[0]
        status_ref.child(status_key).update({"status": "online"})
        print(f"Status updated to 'online' for token: {token}")
    else:
        print(f"No matching status found for token: {token}")


def set_status_offline(token, delay=30):
    # Reference to the 'status' collection
    status_ref = db.reference("status")

    # Find the status entry for the given token
    status_data = status_ref.order_by_child("token").equal_to(token).get()

    # Update the status to 'offline' after a delay if a matching status is found
    if status_data:
        status_key = list(status_data.keys())[0]

        # Sleep for the specified delay in seconds
        time.sleep(delay)

        # Update the status to 'offline'
        status_ref.child(status_key).update({"status": "offline"})
        print(f"Status updated to 'offline' for token: {token}")
    else:
        print(f"No matching status found for token: {token}")


@api_view(["DELETE"])
def delete_token(request, token):
    try:
        # Reference to the 'status' collection
        status_ref = db.reference("status")
        status_data = status_ref.order_by_child("token").equal_to(token).get()

        user_token_ref = db.reference("tokens")
        user_token_data = user_token_ref.order_by_child("token").equal_to(token).get()

        cpu_ref = db.reference("cpu_data")
        cpu_data = cpu_ref.child(token).get()

        network_ref = db.reference("network_data")
        network_data = network_ref.child(token).get()

        system_ref = db.reference("system_data")
        system_data = system_ref.child(token).get()
        hostname = system_data.get('hostname', None)

        installed_apps_ref= db.reference("installed_apps")
        installed_app_data= installed_apps_ref.child(token).get()

        # Delete all matching token entries
        batch = db.batch()

        if status_data:
            for status_key in status_data.keys():
                batch.delete(status_ref.child(status_key))

        if cpu_data:
            batch.delete(cpu_ref.child(token))

        if network_data:
            batch.delete(network_ref.child(token))

        if user_token_data:
            for token_key in user_token_data.keys():
                batch.delete(user_token_ref.child(token_key))

        if system_data:
            # Extract the hostname before deletion
            hostname = system_data.get('hostname', None)
            batch.delete(system_ref.child(token))

        if installed_app_data:
            batch.delete(installed_apps_ref.child(token))

        # Commit the batch operation
        batch.commit()

        if hostname:
            message = "System " + hostname + " was deleted"
        else:
            message = "System was deleted"
        
        type = "delete"
        set_notification(message, type)
        
        return Response({"success": True, "message": "Token deleted successfully"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@csrf_exempt
@require_POST
def store_cpu_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'cpu_data' is the reference to the desired location in your RTDB
        cpu_data_ref = db.reference(f"cpu_data/{token}")

        # Fetch the existing data array or initialize an empty array
        existing_data = cpu_data_ref.child("data").get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        cpu_data_ref.update({"data": existing_data})

        response_data = {
            "status": "success",
            "message": "CPU data stored successfully",
            "data_id": len(existing_data)
            - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)


def hardware_info_page(request, token):
    try:
        cpu_data_ref = db.reference(f"cpu_data/{token}")
        ram_data_ref = db.reference(f"ram_data/{token}")
        disk_data_ref = db.reference(f"disk_data/{token}")
        system_data_ref = db.reference(f"system_data/{token}")

        ram_data = ram_data_ref.get()
        disk_data = disk_data_ref.get()
        system_data = system_data_ref.get()
        cpu_data = cpu_data_ref.get()
        process_data =  cpu_data
        # print ("look here", cpu_data)
        timestamps, cpu_usages = get_cpu_12_hours(process_data.get("data"))
        print ("disk data ", disk_data.get("data", [])[-1])
        # print ("cpu data", process_data.get("data"))

        # print ("ram data", ram_data)
        # print ("cpu_usages data", cpu_usages)

        ram_timestamps, used_swap , free_swap = process_ram_data(ram_data.get("data"))

        if cpu_data:
            # Get the last data section (assuming it's a list of dictionaries)
            latest_cpu_data = cpu_data.get("data", [])[-1]
            latest_ram_data = ram_data.get("data", [])[-1]
            latest_disk_data = disk_data.get("data",[])[-1]

            context = {
                # system data
                "system_name": system_data.get("username", ""),
                "hostname": system_data.get("hostname", ""),
                "operating_system": system_data.get("operating_system", ""),
                

                # cpu data
                "threads": latest_cpu_data.get("threads", ""),
                "cpu_count": latest_cpu_data.get("cpu_count", ""),
                "cpu_usage": latest_cpu_data.get("data", {}).get("cpu_usage", ""),
                "cpu_frequency": latest_cpu_data.get("data", {}).get("cpu_frequency", ""),
                "per_cpu_percent": latest_cpu_data.get("data", {}).get(
                    "per_cpu_percent", ""),
                "timestamp": latest_cpu_data.get("data", {}).get("timestamp", ""),
                "CPUtimestamps": timestamps, 
                "cpu_usages" : cpu_usages,
                "per_cpu_percent_json": json.dumps(latest_cpu_data.get("data", {}).get("per_cpu_percent", [])),

                # ram data 
                "available_memory": latest_ram_data["data"].get("available_memory"),
                "free_memory": latest_ram_data["data"].get("free_memory", ""),
                "free_swap": latest_ram_data["data"].get("free_swap", ""),
                "percent_memory": latest_ram_data["data"].get("percent_memory", ""),
                "percent_swap": latest_ram_data["data"].get("percent_swap", ""),
                "timestamp_ram": latest_ram_data["data"].get("timestamp", ""),
                "total_swap": latest_ram_data["data"].get("total_swap", ""),
                "used_memory": latest_ram_data["data"].get("used_memory", ""),
                "used_swap": latest_ram_data["data"].get("used_swap", ""),
                "total_memory": latest_ram_data.get("total_memory", ""),
                "full_timestamps": ram_timestamps, 
                "used_swap" : used_swap, 
                "free_swap" : free_swap, 

                # disk data
                "total_disk" : latest_disk_data.get("data", {}).get("total_disk", ""),
                "free_disk" : latest_disk_data.get("data", {}).get("free_disk", ""),
                "percent_disk" : latest_disk_data.get("data", {}).get("percent_disk", ""), 
            }

            print()
            print(context)
            return render(request, "hardware_info.html", context)
        else:
            return render(
                request,
                "hardware_info.html",
                {"error_message": f"No data found for token: {token}"},
            )
    except Exception as e:
        return render(
            request, "hardware_info.html", {"error_message": f"An error occurred: {str(e)}"}
        )


# /api/network_data



@csrf_exempt
@require_POST
def store_network_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'cpu_data' is the reference to the desired location in your RTDB
        cpu_data_ref = db.reference(f"network_data/{token}")

        # Fetch the existing data array or initialize an empty array
        existing_data = cpu_data_ref.child("data").get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        cpu_data_ref.update({"data": existing_data})

        response_data = {
            "status": "success",
            "message": "network data stored successfully",
            "data_id": len(existing_data)
            - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)


def network_info_page(request, token):
    try:
        # Assuming 'network_data' is the reference to the desired location in your Firebase
        network_data_ref = db.reference(f"network_data/{token}")
        system_data_ref = db.reference(f"system_data/{token}")

        # Fetch all network data for the specified token
        network_data = network_data_ref.get()
        system_data = system_data_ref.get()
        hostname = system_data['hostname']

        network_data = network_data_ref.get()
        system_data = system_data_ref.get()

        timestamp = []
        download_data = []
        upload_data = []

        download_data2= []
        upload_data2 = []

        last_data_section = []  
        if network_data['data']:
            last_data_section = network_data['data'][-1]['data']            

        if network_data:
    
            for entry in network_data['data']:
                for iface_data in entry['data']:
                    if iface_data['iface'] == 'en0':
                        timestamp.append(entry['timestamp'])
                        download_data.append(iface_data['data']['download'])
                        upload_data.append(iface_data['data']['total_upload'])
                        break  
                    if iface_data['iface']=='lo0': 
                        download_data2.append(iface_data['data']['download'])
                        upload_data2.append(iface_data['data']['total_upload'])


            graph_data = {
                "timestamp": timestamp, 
                "download_data" : download_data, 
                "upload_data" : upload_data, 
                "download_data2" : download_data2, 
                "upload_data2" : upload_data2, 
                "last_data_section" : last_data_section, 
            }

            
            
            print ("looking here",download_data)

            if request.headers.get("Content-Type") == "application/json":
                # Return JSON response for API requests
                response_data = {
                    "success": True,
                    "hostname": hostname,
                    "all_data_sections": network_data.get("data", []),
                }
                return JsonResponse(response_data)
            else:
                # Render HTML template for regular requests
                return render(request, "network_info.html", graph_data)

        else:
            response_data = {
                "success": False,
                "message": f"No data found for network with token: {token}",
            }
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse(response_data, status=404)
            else:
                return render(
                    request,
                    "network_info.html",
                    {"error_message": f"No data found for network with token: {token}"},
                )

    except Exception as e:
        response_data = {
            "success": False,
            "message": f"An error occurred: {str(e)}",
        }
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse(response_data, status=500)
        else:
            return render(
                request,
                "network_info.html",
                {"error_message": f"An error occurred: {str(e)}"},
            )

@firebase_auth_required
def network_dashboard_view(request):
    tokens_ref = db.reference("tokens")
    status_ref = db.reference("status")    
    tokens_data = tokens_ref.order_by_child("token").get()
    status_data = status_ref.order_by_child("token").get()

    system_ref = db.reference("system_data")
    system_data = system_ref.order_by_child("token").get()
    

    tokens = []
    for token_key, token in tokens_data.items():
        status_key = next(
            (
                key
                for key, value in status_data.items()
                if value["token"] == token["token"]
            ),
            None,
        )
        status = status_data.get(status_key, {}) if status_key else {}
        system_details = system_data.get(token["token"], {}) 


        token_details = {
            "token": token["token"],
            "network_info": f'/api/network_info/{token["token"]}/',
            "status": status.get("status", "N/A"),
            "system_data": system_details
        }
        # print(token_details)
        tokens.append(token_details)

    return render(request, "network_dashboard.html", {"tokens": tokens})


@firebase_auth_required
def installed_apps_dashboard_view(request):
    tokens_ref = db.reference("tokens")
    status_ref = db.reference("status")

    tokens_data = tokens_ref.order_by_child("token").get()
    status_data = status_ref.order_by_child("token").get()

    system_ref = db.reference("system_data")
    system_data = system_ref.order_by_child("token").get()


    tokens = []
    for token_key, token in tokens_data.items():
        status_key = next(
            (
                key
                for key, value in status_data.items()
                if value["token"] == token["token"]
            ),
            None,
        )
        status = status_data.get(status_key, {}) if status_key else {}
        system_details = system_data.get(token["token"], {}) 

        token_details = {
            "token": token["token"],
            "details_url": f'/token-details/{token["token"]}/',
            "status": status.get("status", "N/A"),
            "system_data": system_details # Include system data
        }
        print(token_details)
        tokens.append(token_details)

    return render(request, "installed_apps_dashboard.html", {"tokens": tokens})

def index_view(request):
    return render(request, 'index.html')

def blank_view(request):
    return render(request, 'blank.html')

@csrf_exempt
@require_POST
def store_system_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        system_data_ref = db.reference(f"system_data/{token}")

        # Overwrite existing data with new data
        system_data_ref.set(data)

        response_data = {
            "status": "success",
            "message": "System data stored successfully",
            "data_id": token  # Use token as data_id
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)


def set_notification(message, type):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    read = False
    context = {
        "timestamp": timestamp, 
        "message": message, 
        "type": type, 
        "read": read
    }

    notification_ref = db.reference("notifications")
    notification_ref.push(context)


def reports_view(request):
    tokens_ref = db.reference("tokens")
    tokens_data = tokens_ref.order_by_child("token").get()
    system_ref = db.reference("system_data")
    system_data = system_ref.order_by_child("token").get()

    tokens = []
    for token_key, token in tokens_data.items():
        system_details = system_data.get(token["token"], {})  # Fetch system details based on token

        # Create a dictionary with token details, status, and system data
        token_details = {
            "token": token["token"],
            "generate_report": f'/api/generate_report/{token["token"]}/',
            "system_data": system_details  # Include system data
        }
        tokens.append(token_details)

    
    return render(request, 'report.html', {'tokens': tokens})



def generate_reports(request, token): 
    tokens_ref = db.reference("tokens")
    tokens_data = tokens_ref.order_by_child("token").get()
    cpu_data_ref = db.reference(f"cpu_data/{token}")
    ram_data_ref = db.reference(f"ram_data/{token}")
    disk_data_ref = db.reference(f"disk_data/{token}")        
    system_data_ref = db.reference(f"system_data/{token}")
    installed_apps_ref = db.reference(f"installed_apps/{token}")
    ram_data = ram_data_ref.get()
    disk_data = disk_data_ref.get()
    system_data = system_data_ref.get()
    cpu_data = cpu_data_ref.get() 
    installed_app_data=  installed_apps_ref.get()

    average_cpu_data = cpu_data.get("data", [])[-1]
    average_ram_data = ram_data.get("data", [])[-1]
    average_disk_data = disk_data.get("data",[])[-1]

    tokens = []
    token_details = {
        "generate_report": f'/api/generate_pdf_report/{token}/',
        "system_data": system_data , # Include system data,
        "cpu_data" :average_cpu_data , 
        "ram_data" :average_ram_data , 
        "disk_data": average_disk_data, 
        "installed_app_data": installed_app_data, 
    }

    tokens.append(token_details)
    
    # Get the hostname from system_data
    hostname = system_data.get("hostname", "")

    return render(request, 'generate_report.html', {'tokens': tokens})


 
def terminal_view(request): 

    tokens_ref = db.reference("tokens")
    tokens_data = tokens_ref.order_by_child("token").get()
    system_ref = db.reference("system_data")
    system_data = system_ref.order_by_child("token").get()

    tokens = []
    for token_key, token in tokens_data.items():
        system_details = system_data.get(token["token"], {})  # Fetch system details based on token

        # Create a dictionary with token details, status, and system data
        token_details = {
            "token": token["token"],
            "generate_terminal": f'/api/generate_terminal/{token["token"]}/',
            "system_data": system_details  # Include system data
        }
        tokens.append(token_details)
    

    return render (request, 'terminal.html',  {'tokens': tokens})

@csrf_exempt
def generate_terminal(request, token):
    commands_ref = db.reference(f"commands/{token}")
    system_data_ref = db.reference(f"system_data/{token}")
    system_data = system_data_ref.get()

    cpu_data_ref = db.reference(f"cpu_data/{token}")
    ram_data_ref = db.reference(f"ram_data/{token}")
    disk_data_ref = db.reference(f"disk_data/{token}")

    cpu_data = cpu_data_ref.get()
    ram_data = ram_data_ref.get()
    disk_data = disk_data_ref.get()
    system_data = system_data_ref.get()

    latest_cpu_data = cpu_data.get("data", [])[-1]
    latest_ram_data = ram_data.get("data", [])[-1]
    latest_disk_data = disk_data.get("data",[])[-1]


    if request.method == 'POST':
        command = request.POST.get('command')
        if command:
            commands_data = commands_ref.get() or []
            command_count = len([cmd for cmd in commands_data if cmd is not None])

            # Construct a numbered command entry with an ID
            command_entry = {
                "id": command_count + 1,  # Assigning an ID
                "command": command,
                "executed": False,
                "response": ""
            }

            # Save the numbered command to Firebase Realtime Database under the token
            commands_ref.child(str(command_count + 1)).set(command_entry)
        
        return redirect('generate_terminal', token=token)

    commands_data = commands_ref.get() or []
    commands_list = [
        command for command in commands_data if command is not None
    ]

    return render(request, 'generate_terminal.html', {
        'token': token,
        'commands': commands_list, 
        "system_data": system_data,
        "cpu_usage": latest_cpu_data.get("data", {}).get("cpu_usage", ""),
        "percent_memory": latest_ram_data["data"].get("percent_memory", ""),
        "percent_disk" : latest_disk_data.get("data", {}).get("percent_disk", ""), 

    })

def check_issued_commands(request, token):
    # Reference to the Firebase Realtime Database node where you store commands
    command_ref = db.reference("/commands")
    
    # Get a snapshot of the commands node
    commands_snapshot = command_ref.get()
    
    # List to store unexecuted commands matching the token ID
    unexecuted_commands = []
    
    # Check if the snapshot is not None and if the token exists in the commands snapshot
    if commands_snapshot and token in commands_snapshot:
        # Iterate through each command in the token's list
        for command_info in commands_snapshot[token][1:]:
            if command_info and not command_info.get("executed", True):
                # Append the unexecuted command to the list
                unexecuted_commands.append(command_info)
    
    return JsonResponse(unexecuted_commands, safe=False)


@csrf_exempt
@require_POST
def send_executed_commands(request, token):
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        
        # Validate the data
        if not isinstance(data, list):
            return JsonResponse({"status": "error", "message": "Invalid data format. Expected a list."}, status=400)

        # Reference to the Firebase Realtime Database node where commands are stored
        command_ref = db.reference(f"/commands/{token}")

        # Fetch the existing commands for the given token
        existing_commands = command_ref.get()
        if existing_commands is None:
            return JsonResponse({"status": "error", "message": "No commands found for the given token."}, status=404)

        # Check if the first element is None and exclude it from processing
        if existing_commands and existing_commands[0] is None:
            existing_commands = existing_commands[1:]

        # Update the commands with the data provided
        for command_update in data:
            command_id = command_update.get("id")
            if command_id is None:
                continue

            # Find the command with the given ID in the existing commands
            for existing_command in existing_commands:
                if existing_command and existing_command.get("id") == command_id:
                    existing_command.update(command_update)
                    break

        # Prepend None if it was originally part of the data
        if command_ref.get() and command_ref.get()[0] is None:
            existing_commands.insert(0, None)

        # Update the database with the modified commands
        command_ref.set(existing_commands)

        return JsonResponse({"status": "success", "message": "Commands updated successfully."})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON data."}, status=400)

    except Exception as e:
        # Log the error message
        print(f"An error occurred: {str(e)}")
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)


@csrf_exempt
@require_POST
def store_ram_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'cpu_data' is the reference to the desired location in your RTDB
        cpu_data_ref = db.reference(f"ram_data/{token}")

        # Fetch the existing data array or initialize an empty array
        existing_data = cpu_data_ref.child("data").get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        cpu_data_ref.update({"data": existing_data})

        response_data = {
            "status": "success",
            "message": "RAM data stored successfully",
            "data_id": len(existing_data)
            - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)
    

@csrf_exempt
@require_POST
def store_disk_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'cpu_data' is the reference to the desired location in your RTDB
        cpu_data_ref = db.reference(f"disk_data/{token}")

        # Fetch the existing data array or initialize an empty array
        existing_data = cpu_data_ref.child("data").get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        cpu_data_ref.update({"data": existing_data})

        response_data = {
            "status": "success",
            "message": "DISK data stored successfully",
            "data_id": len(existing_data)
            - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)    
    


@csrf_exempt
@require_POST
def store_ram_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'cpu_data' is the reference to the desired location in your RTDB
        ram_data_ref = db.reference(f"ram_data/{token}")

        # Fetch the existing data array or initialize an empty array
        existing_data = ram_data_ref.child("data").get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        ram_data_ref.update({"data": existing_data})

        response_data = {
            "status": "success",
            "message": "RAM data stored successfully",
            "data_id": len(existing_data)
            - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)
    


@csrf_exempt
@require_POST
def store_disk_data(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")

        if not token:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'disk_data' is the reference to the desired location in your RTDB
        disk_data_ref = db.reference(f"disk_data/{token}")

        # Fetch the existing data array or initialize an empty array
        existing_data = disk_data_ref.child("data").get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        disk_data_ref.update({"data": existing_data})

        response_data = {
            "status": "success",
            "message": "CPU data stored successfully",
            "data_id": len(existing_data)
            - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)    
    

def generate_pdf_report(request, token):    

    cpu_data_ref = db.reference(f"cpu_data/{token}")
    ram_data_ref = db.reference(f"ram_data/{token}")
    disk_data_ref = db.reference(f"disk_data/{token}")        
    system_data_ref = db.reference(f"system_data/{token}")
    installed_apps_ref = db.reference(f"installed_apps/{token}")
    ram_data = ram_data_ref.get()
    disk_data = disk_data_ref.get()
    system_data = system_data_ref.get()
    cpu_data = cpu_data_ref.get() 
    installed_app_data=  installed_apps_ref.get()

    average_cpu_data = cpu_data.get("data", [])[-1]
    average_ram_data = ram_data.get("data", [])[-1]
    average_disk_data = disk_data.get("data",[])[-1]

    tokens = []
    token_details = {
        "generate_report": f'/api/generate_pdf_report/{token}/',
        "system_data": system_data , # Include system data,
        "cpu_data" :average_cpu_data , 
        "ram_data" :average_ram_data , 
        "disk_data": average_disk_data, 
        "installed_app_data": installed_app_data, 
    }

    tokens.append(token_details)
    
    # Get the hostname from system_data
    hostname = system_data.get("hostname", "")

    # Render the HTML template to a string
    html_string = render(request, 'report_template.html', {'tokens': tokens}).content.decode('utf-8')

    # Create a BytesIO buffer to receive the PDF data
    pdf_buffer = BytesIO()

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        src=html_string,
        dest=pdf_buffer
    )

    # If there was an error during conversion, log it or handle it
    if pisa_status.err:
        return HttpResponse('We had some errors with your request')

    # Return the generated PDF file
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Set the notification message with the hostname
    message = f"Report generated for: {hostname}"
    set_notification(message, "New_report")

    return response

