<<<<<<< Updated upstream
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from myapp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
import json
from rest_framework.decorators import api_view
from django.utils.crypto import get_random_string
from .models import *
from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm
from django.views.decorators.http import require_POST
from pymongo import MongoClient
from datetime import datetime
from django.contrib.auth.models import User


# Token Verification and Status Update
=======
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from myapp.models import *
from pymongo import MongoClient
import json, time
from rest_framework.decorators import api_view
from .models import *
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.views.decorators.http import require_POST
from myapp.methods import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .functions import *
import logging
from bson import ObjectId

>>>>>>> Stashed changes
@csrf_exempt
def check_token(request, token):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["myapp_apitoken"]

        # Check if the token exists in MongoDB
        token_exists = collection.find_one({"token": token}) is not None

        update_token_status(token)
<<<<<<< Updated upstream

        return JsonResponse({"exists": token_exists})

=======
        set_notification(f"Token {token} was checked.", "token_check")

        return JsonResponse({"exists": token_exists})

>>>>>>> Stashed changes
    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred while checking the token: {str(e)}"},
            status=500,
        )


@csrf_exempt
def check_username(request, username):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["auth_user"]

        # Check if the username exists in MongoDB
        user_exists = collection.find_one({"username": username}) is not None
<<<<<<< Updated upstream
=======

        set_notification(f"Username {username} was checked.", "username_check")

>>>>>>> Stashed changes
        return JsonResponse({"exists": user_exists})

    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred while checking the username: {str(e)}"},
            status=500,
        )


@csrf_exempt
def update_token_status(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            token = data.get("token")

            client = MongoClient("mongodb://localhost:27017/")
            db = client["commandcontrol"]
            collection = db["myapp_apitoken"]

            # Find the APIToken entry for the given token
            token_entry = collection.find_one({"token": token})

            # Update the status to 'online' if a matching token is found
            if token_entry:
                collection.update_one(
                    {"_id": token_entry["_id"]},
                    {"$set": {"status": "online", "last_active": timezone.now()}},
                )
                print(f"Status updated to 'online' for token: {token}")
            else:
                print(f"No matching token found for status update: {token}")

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "message": "Invalid request method"})
    except Exception as e:
        print(f"Error updating status for token: {token}: {e}")
        return JsonResponse({"success": False, "message": str(e)})
<<<<<<< Updated upstream
=======


@csrf_exempt
def set_status_offline(request):
    if request.method == "POST":
        try:
            json_data = json.loads(request.body)
            token = json_data.get("token")
            token_entry = APIToken.objects.filter(token=token).first()
            if token_entry:
                token_entry.status = "offline"
                token_entry.save()
                print(f"\nStatus updated to 'offline' for token: {token}")
                return JsonResponse({"success": True})
            else:
                print(f"\nNo matching token found for status update: {token}")
                return JsonResponse({"success": False, "message": "Token not found"})
        except Exception as e:
            print(f"\nError updating status for token: {token}: {e}")
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})
>>>>>>> Stashed changes


@csrf_exempt
def set_status_offline(request):
    if request.method == "POST":
<<<<<<< Updated upstream
        try:
            json_data = json.loads(request.body)
            token = json_data.get("token")
            token_entry = APIToken.objects.filter(token=token).first()
            if token_entry:
                token_entry.status = "offline"
                token_entry.save()
                print(f"\nStatus updated to 'offline' for token: {token}")
                return JsonResponse({"success": True})
            else:
                print(f"\nNo matching token found for status update: {token}")
                return JsonResponse({"success": False, "message": "Token not found"})
        except Exception as e:
            print(f"\nError updating status for token: {token}: {e}")
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})
=======
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
>>>>>>> Stashed changes


# Login and Logout
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                return render(
                    request,
                    "registration/login.html",
                    {"form": form, "error": "Invalid username or password"},
                )
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


<<<<<<< Updated upstream
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})
=======
@login_required
def dashboard_view(request):
    # Fetch all token data
    tokens_data = APIToken.objects.all()

    tokens = []

    online_count = 0

    notifications = []

    for token in tokens_data:

        status = token.status

        system_data = SystemData.objects.filter(token=token).first()

        username = None
        hostname = None
        operating_system = None
        operating_system_version = None

        if system_data:

            username = system_data.username
            hostname = system_data.hostname
            operating_system = system_data.operating_system
            operating_system_version = system_data.operating_system_version

        if status == "online":
            online_count += 1

        token_details = {
            "token": token.token,
            "username": username,
            "hostname": hostname,
            "operating_system": operating_system,
            "operating_system_version": operating_system_version,
            "token_details": f"/api/token_details/{token.token}/",
            "cpu_info": f"/api/cpu_info/{token.token}/",
            "network_info": f"/api/network_info/{token.token}/",
            "system_data": system_data,
            "status": status if status else "offline",
        }

        tokens.append(token_details)
    
    notifications_data = Notifications.objects.all()

    for notification in notifications_data:

        notification_details = {
            "timestamp": notification.timestamp,
            "message": notification.message,
            "type": notification.type,
            "read": notification.read,
        }

        notifications.append(notification_details)

    return render(request, "dashboard.html", {"tokens": tokens, "online_count": online_count, "notifications": notifications})


@login_required
def cpu_dashboard_view(request):
    tokens_data = APIToken.objects.all()

    tokens = []

    for token in tokens_data:

        status = token.status

        token_details = {
            "token": token.token,
            "cpu_info": f"/api/cpu_info/{token.token}/",
            "status": status if status else "offline",
        }
        print(token_details)
        tokens.append(token_details)

    return render(request, "cpu_dashboard.html", {"tokens": tokens})

def hardware_info_page(request, token):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client['commandcontrol']

        cpu_collection = db['myapp_cpuinfo']
        ram_collection = db['myapp_raminfo']
        disk_collection = db['myapp_diskinfo']
        system_collection = db['myapp_systemdata']

        cpu_data = list(cpu_collection.find({"token_id": token}, sort=[("_id", -1)]))
        print(f"\n\n\n\nCPU Data for {token}: {cpu_data} ")
        ram_data = list(ram_collection.find({"token_id": token}, sort=[("_id", -1)]))
        print(f"\n\n\n\nRAM Data for {token}: {ram_data} ")
        disk_data = list(disk_collection.find({"token_id": token}, sort=[("_id", -1)]))
        print(f"\n\n\n\nDisk Data for {token}: {disk_data} ")
        system_data = system_collection.find_one({"token_id": token})
        print(f"\n\n\n\nSystem Data for {token}: {system_data} ")

        if not cpu_data or not ram_data or not disk_data:
            return render(request, "hardware_info.html", {"error_message": f"No data found for the specified token: {token}"})
>>>>>>> Stashed changes

        timestamps, cpu_usages = get_cpu_12_hours(cpu_data)
        ram_timestamps, used_swap, free_swap = process_ram_data(ram_data)

<<<<<<< Updated upstream
def logout_view(request):
    logout(request)
    return redirect("login")
=======
        latest_cpu_data = cpu_data[0]
        latest_ram_data = ram_data[0]
        latest_disk_data = disk_data[0]

        context = {
            "token": token,
            "system_name": system_data['username'],
            "hostname": system_data['hostname'],

            "threads": latest_cpu_data['threads'],
            "cpu_count": latest_cpu_data['cpu_count'],
            "cpu_percent": latest_cpu_data['cpu_percent'],
            "cpu_freq_value": latest_cpu_data['cpu_freq_value'],
            "percent_per_cpu": latest_cpu_data['percent_per_cpu'],
            "timestamp": latest_cpu_data['timestamp'],
            "CPUtimestamps": timestamps,
            "cpu_usages": cpu_usages,
            "percent_per_cpu_json": json.dumps(latest_cpu_data['percent_per_cpu']),

            "available_memory": latest_ram_data['available_memory'],
            "free_memory": latest_ram_data['free_memory'],
            "free_swap": latest_ram_data['free_swap'],
            "percent_memory": latest_ram_data['percent_memory'],
            "percent_swap": latest_ram_data['percent_swap'],
            "timestamp_ram": latest_ram_data['timestamp'],
            "total_swap": latest_ram_data['total_swap'],
            "used_memory": latest_ram_data['used_memory'],
            "used_swap": latest_ram_data['used_swap'],
            "total_memory": latest_ram_data['total_memory'],
            "full_timestamps": ram_timestamps,
            "used_swap": used_swap,
            "free_swap": free_swap,
>>>>>>> Stashed changes

            "total_disk": latest_disk_data['total_disk'],
            "free_disk": latest_disk_data['free_disk'],
            "percent_disk": latest_disk_data['percent_disk'],
        }
        return render(request, "hardware_info.html", context)

<<<<<<< Updated upstream
# Installed Apps Storage and Viewing
=======
    except Exception as e:
        return render(request, "hardware_info.html", {"error_message": str(e)})

@api_view(["DELETE"])
def delete_token(request, token):
    try:
        # connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]

        # Delete data from network stats collection
        db["myapp_networkstats"].delete_many({"token_id": token})

        # Delete data from CPU info collection
        db["myapp_cpuinfo"].delete_many({"token_id": token})

        # Delete data from installed apps collection
        db["myapp_installedapp"].delete_many({"token_id": token})

        # Delete data from System Data Collection
        system_data = db["myapp_systemdata"].find_one_and_delete({"token_id": token})

        # Delete token from APIToken collection
        db["myapp_apitoken"].delete_one({"token": token})

        if system_data:
            set_notification(f"System with {system_data['hostname']} was deleted.", "delete")

        return JsonResponse({"success": True, "message": "System deleted successfully"})

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"An error occurred: {str(e)}"}, status=500
        )


>>>>>>> Stashed changes
@csrf_exempt
@require_POST
def store_installed_apps(request):
    try:
        print("\nReceived request to store installed apps...")
        data = json.loads(request.body)
        token_value = data.get("token")

        if not token_value:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)

        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            response_data = {
                "status": "error",
                "message": "Invalid token",
            }
            return JsonResponse(response_data, status=400)

        installed_apps_list = data.get("data", [])
        if not installed_apps_list:
            response_data = {
                "status": "error",
                "message": "Installed apps data is missing",
            }
            return JsonResponse(response_data, status=400)

        # Create or update the InstalledApp object
        installed_apps, created = InstalledApp.objects.update_or_create(
            token=token, defaults={"data": installed_apps_list}
        )

        response_data = {
            "status": "success",
            "message": "Installed apps data stored successfully",
        }

        print("\nSending success response...")
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        print("Invalid JSON data. Sending error response...")
        response_data = {
            "status": "error",
            "message": "Invalid JSON data",
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        print(f"An error occurred: {str(e)}. Sending error response...")
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)


def token_details_view(request, token):
<<<<<<< Updated upstream
    # fetch installed apps data for the specific token
    installed_apps_data = InstalledApp.objects.filter(token=token).values_list(
        "data", flat=True
    )

    # Convert the QuerySet to a list
    installed_apps_data = list(installed_apps_data)

    return render(
        request,
        "token_details.html",
        {"token": token, "installed_apps_data": installed_apps_data},
    )


# Dashboard View and Delete Button
@login_required
def dashboard_view(request):
    # Retrieve token data from MongoDB
    tokens_data = APIToken.objects.all()

    # Create a list of tokens with details
    tokens = []
    for token in tokens_data:
        # Get the status of the token
        status = token.status
        # Get the username of the token
        username = token.username
        # Create a dictionary with token details, status and last active
        token_details = {
            "token": token.token,
            "username": username,
            "details_url": f"/token-details/{token.token}/",
            "cpu_info": f"/api/cpu_info/{token.token}/",
            "network_info": f"/api/network_info/{token.token}/",
            "status": status if status else "offline",
        }

        tokens.append(token_details)

    return render(request, "dashboard.html", {"tokens": tokens})


@api_view(["DELETE"])
def delete_token(request, token):
    try:
        # connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]

        # Delete data from network stats collection
        db["myapp_networkstats"].delete_many({"token_id": token})

        # Delete data from CPU info collection
        db["myapp_cpuinfo"].delete_many({"token_id": token})

        # Delete data from installed apps collection
        db["myapp_installedapp"].delete_many({"token_id": token})

        # Delete token from APIToken collection
        db["myapp_apitoken"].delete_one({"token": token})

        return JsonResponse({"success": True, "message": "Token deleted successfully"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"An error occurred: {str(e)}"}, status=500
        )


# CPU Stats Storage and Viewing
=======
    # Connect to MongoDB

    client = MongoClient("mongodb://localhost:27017/")
    db = client["commandcontrol"]
    apps_collection = db["myapp_installedapp"]
    system_data_collection = db["myapp_systemdata"]

    # Fetch system data and installed apps data for the specified token
    system_data = system_data_collection.find_one({"token_id": token})
    apps_data = apps_collection.find_one({"token_id": token})

    installed_apps_data = apps_data.get("data", []) if apps_data else []

    name_filter = request.GET.get('name', '')
    version_filter = request.GET.get('version', '')
    last_modified_filter = request.GET.get('last_modified', '')

    if name_filter:
        installed_apps_data = [app for app in installed_apps_data if name_filter.lower() in app.get("name", "").lower()]
    
    if version_filter:
        installed_apps_data = [app for app in installed_apps_data if version_filter.lower() in app.get("version", "").lower()]
    
    if last_modified_filter:
        try:
            last_modified_date = datetime.strptime(last_modified_filter, "%Y-%m-%d")
            installed_apps_data = [app for app in installed_apps_data if datetime.strptime(app.get('lastModified', ''), '%Y-%m-%dT%H:%M:%SZ').date() == last_modified_date.date()]

        except ValueError:
            return render(request, "token_details.html", {"error_message": "Invalid date format. Please use YYYY-MM-DD."})
        
    return render(request, "token_details.html", {
        "system_data": system_data,
        "installed_apps": installed_apps_data,
        "request": request,
    },
)


>>>>>>> Stashed changes
@csrf_exempt
def store_cpu_data(request):
    try:
        print("\nReceived request to store CPU data...")

        # Parse request body
        data = json.loads(request.body)
        token_value = data.get("token")

        if not token_value:
            print("\nToken is required. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Token is required"}, status=400
            )

        # Check if the token exists
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            print("\nInvalid token. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Invalid token"}, status=400
            )

        cpu_data = data.get("data")
        if not cpu_data:
            print("\nCPU data is missing. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "CPU data is missing"}, status=400
            )

        # Extract CPU information from the data
        cpu_count = data.get("cpu_count")
        threads = data.get("threads")
        cpu_percent = cpu_data.get("cpu_percent")
        cpu_freq_value = cpu_data.get("cpu_freq_value")
        percent_per_cpu = cpu_data.get("percent_per_cpu")

        # convert timestamp to timezone-aware datetime object
        timestamp_str = cpu_data.get("timestamp")
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        timestamp_aware = timezone.make_aware(
            timestamp, timezone.get_current_timezone()
        )

        # Create new CPUInfo object
        cpu_info = CPUInfo.objects.create(
            token=token,
            timestamp=timestamp_aware,
            cpu_count=cpu_count,
            threads=threads,
            cpu_percent=cpu_percent,
            cpu_freq_value=cpu_freq_value,
            percent_per_cpu=percent_per_cpu,
        )

        print("\nCreated new CPU data:", cpu_info)
        response_data = {
            "status": "success",
            "message": "New CPU data stored successfully",
            "data_id": cpu_info.id,
        }

        print("\nSending success response...")
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        print("\nInvalid JSON data. Sending error response...")
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON data"}, status=400
        )

    except Exception as e:
        print(f"An error occurred: {str(e)}. Sending error response...")
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"}, status=500
        )


def cpu_info_page(request, token):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["myapp_cpuinfo"]

        # Fetch all CPU data for the specified token
        cpu_data = list(collection.find({"token_id": token}, sort=[("_id", -1)]))
<<<<<<< Updated upstream
=======
        system_data = SystemData.objects.filter(token=token).first()
>>>>>>> Stashed changes

        if cpu_data:
            # Get the last fetched CPU data
            last_cpu_data = cpu_data[0]
            percent_per_cpu_values = last_cpu_data.get("percent_per_cpu", [])

<<<<<<< Updated upstream
=======
            hostname = system_data.hostname
            username = system_data.username
            operating_system = system_data.operating_system

>>>>>>> Stashed changes
            labels = [f"CPU {i+1}" for i in range(len(percent_per_cpu_values))]
            percent_per_cpu_values = [
                value
                for value in percent_per_cpu_values
                if isinstance(value, (int, float))
            ]
            context = {
                "timestamp": last_cpu_data.get("timestamp"),
                "cpu_count": last_cpu_data.get("cpu_count"),
                "threads": last_cpu_data.get("threads"),
                "cpu_percent": last_cpu_data.get("cpu_percent"),
                "cpu_freq_value": last_cpu_data.get("cpu_freq_value"),
                "percent_per_cpu": last_cpu_data.get("percent_per_cpu"),
<<<<<<< Updated upstream
=======
                "hostname": hostname,
                "username": username,
                "operating_system": operating_system,
>>>>>>> Stashed changes
                "percent_per_cpu_labels": labels,
                "percent_per_cpu_values": percent_per_cpu_values,
            }

            return render(request, "cpu_info.html", context)
        else:
            return render(
                request,
                "cpu_info.html",
                {"error_message": f"No data found for token: {token}"},
            )
    except Exception as e:
        return render(
            request,
            "cpu_info.html",
            {"error_message": f"An error occurred: {str(e)}"},
        )


<<<<<<< Updated upstream
# Network Stats Storage and Viewing
=======
>>>>>>> Stashed changes
@csrf_exempt
def store_network_data(request):
    try:
        print("\nReceived request to store network data...")
        data = json.loads(request.body)
        token_value = data.get("token")

        if not token_value:
            response_data = {
                "status": "error",
                "message": "Token is required in the JSON data.",
            }
            return JsonResponse(response_data, status=400)
        
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            response_data = {
                "status": "error",
                "message": "Invalid token.",
            }
            return JsonResponse(response_data, status=400)
        
        network_data_list = data.get("data", [])
        if not network_data_list:
            response_data = {
                "status": "error",
                "message": "Network data is missing.",
            }
            return JsonResponse(response_data, status=400)
        
        for network_data in network_data_list:
            iface = network_data.get("iface")
            timestamp_str = network_data.get("timestamp")
            if not iface or not timestamp_str:
                print("Interface name or Timestamp is missing. Skipping...")
                continue

<<<<<<< Updated upstream
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            response_data = {
                "status": "error",
                "message": "Invalid token",
            }
            return JsonResponse(response_data, status=400)

        network_data_list = data.get("data", [])
        if not network_data_list:
            response_data = {
                "status": "error",
                "message": "Network data is missing",
            }
            return JsonResponse(response_data, status=400)

        # Combine all interface data into a single dictionary
        all_interface_data = {}
        for network_data in network_data_list:
            timestamp_str = network_data.get("timestamp")
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp_aware = timezone.make_aware(
                timestamp, timezone.get_current_timezone()
            )
            iface = network_data.get("iface")
            if not iface or not timestamp_aware:
                print("Interface name and Timestamp is missing. Skipping...")
                continue

            all_interface_data[iface] = network_data.get("data", {})

        # Create a new NetworkStats object for each request
        NetworkStats.objects.create(
            token=token, timestamp=timestamp_aware, data=all_interface_data
        )

        response_data = {
            "status": "success",
            "message": "Network data stored successfully",
=======
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp_aware = timezone.make_aware(
                timestamp, timezone.get_current_timezone()
            )

            network_info = NetworkStats.objects.create(
                token=token,
                timestamp=timestamp_aware,
                data = network_data,
            )

        response_data = {
            "status": "success",
            "message": "Network data stored successfully.",
>>>>>>> Stashed changes
        }

        print("\nSending success response...")
        return JsonResponse(response_data)
    
    except json.JSONDecodeError:
<<<<<<< Updated upstream
        print("Invalid JSON data. Sending error response...")
=======
        print("\nInvalid JSON data. Sending error response...")
>>>>>>> Stashed changes
        response_data = {
            "status": "error",
            "message": "Invalid JSON data.",
        }
        return JsonResponse(response_data, status=400)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}. Sending error response...")
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        return JsonResponse(response_data, status=500)

def network_info_page(request, token):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["myapp_networkstats"]

<<<<<<< Updated upstream
        # Fetch all network data for the specified token
        network_data = collection.find({"token_id": token})

        if network_data:
            network_info = []

            # Iterate over each network entity
            for entity in network_data:
                entity_data = {"timestamp": entity.get("timestamp"), "interfaces": []}

                # Iterate over each interface and its data
                for iface, data in entity.get("data", {}).items():
                    entity_data["interfaces"].append({"interface": iface, "data": data})

                network_info.append(entity_data)

            context = {
                "network_info": network_info,
            }

            if request.headers.get("Content-Type") == "application/json":
                # Return JSON response for API requests
                response_data = {
                    "status": True,
                    "network_info": network_info,
                }
                return JsonResponse(response_data)
            else:
                return render(request, "network_info.html", context)
        else:
            response_data = {
                "success": False,
                "message": f"No data found for token: {token}",
            }
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse(response_data, status=404)
            else:
                return render(
                    request,
                    "network_info.html",
                    {"error_message": f"No data found for token: {token}"},
                )
=======
        network_data_cursor = collection.find({"token_id": token})
        network_data = list(network_data_cursor)

        network_info = []

        for entity in network_data:
            interface_data = entity.get("data", {})
            if interface_data.get("iface") in ["en0", "lo0"]:
                entity_data = {
                    "timestamp": entity.get("timestamp"),
                    "interfaces": [interface_data]
                }
                network_info.append(entity_data)

        context = {
            "network_info": network_info,
        }

        if request.headers.get("Content-Type") == "application/json":
            response_data = {
                "status": "success",
                "network_info": network_info,
            }
            return JsonResponse(response_data)
        else:
            return render(request, "network_info.html", context)
    
>>>>>>> Stashed changes
    except Exception as e:
        response_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse(response_data, status=500)
        else:
<<<<<<< Updated upstream
            return render(
                request,
                "network_info.html",
                {"error_message": f"An error occurred: {str(e)}"},
            )
=======
            return render(request, "network_info.html", {"error_message": str(e)})
        
@login_required
def hardware_dashboard_view(request):
    tokens_data = APIToken.objects.all()

    tokens = []
    online_count = 0

    for token in tokens_data:
        status = token.status
        system_data = SystemData.objects.filter(token=token).first()
        cpu_data = CPUInfo.objects.filter(token=token)
        ram_data = RamInfo.objects.filter(token=token)
        disk_data = DiskInfo.objects.filter(token=token)

        avg_count, avg_usage, avg_freq = average_cpu_metrics(cpu_data)
        ram_avg_size, ram_avg_usage, ram_avg_swap = average_ram_metrics(ram_data)
        total_disk_size, total_disk_usage, total_percent_disk = average_disk_metrics(disk_data)

        username = None
        hostname = None

        if system_data:
            username = system_data.username
            hostname = system_data.hostname

        if status == "online":
            online_count += 1

        token_details = {
            "token": token.token,
            "username": username,
            "hostname": hostname,
            "hardware_info": f"/api/hardware_info/{token.token}/",
            "status": status if status else "offline",
            "system_data": system_data,
        }

        tokens.append(token_details)
    
    data = {
        "tokens": tokens,
        "online_count": online_count,

        "avg_count": avg_count,
        "avg_usage": avg_usage,
        "avg_freq": avg_freq,

        "ram_avg_size": ram_avg_size,
        "ram_avg_usage": ram_avg_usage,
        "ram_avg_swap": ram_avg_swap,

        "total_disk_size": total_disk_size,
        "total_disk_usage": total_disk_usage,
        "total_percent_disk": total_percent_disk,
    }

    return render(request, "hardware_dashboard.html", data)


@login_required
def network_dashboard_view(request):
    tokens = APIToken.objects.all()

    token_details = []
    for token in tokens:
        status = token.status

        system_data = SystemData.objects.filter(token=token.token).first()

        token_detail = {
            "token": token.token,
            "network_info": f"/api/network_info/{token.token}/",
            "status": status if status else "offline",
            "system_data": system_data,
        }

        token_details.append(token_detail)

    return render(request, "network_dashboard.html", {"tokens": token_details})

@login_required
def installed_apps_dashboard_view(request):

    tokens = APIToken.objects.all()

    token_details_list = []

    for token in tokens:

        status = token.status

        token_detail = {
            "token": token.token,
            "token_details": f"/api/token_details/{token.token}/",
            "status": status if status else "offline",
        }

        token_details_list.append(token_detail)

    return render(request, "installed_apps_dashboard.html", {"token_detail_list": token_details_list})


def index_view(request):
    return render(request, "index.html")


def blank_view(request):
    return render(request, "blank.html")


@csrf_exempt
def store_system_data(request):
    try:
        print("\nReceived request to store system data...")
        # Parse JSON data from request body
        data = json.loads(request.body)

        # Extract token from JSON data
        token_value = data.get("token")

        # Validate token presence
        if not token_value:
            return JsonResponse(
                {"status": "error", "message": "Token is required in the JSON data."},
                status=400,
            )

        # Check if APIToken exists
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            return JsonResponse(
                {"status": "error", "message": "Invalid token."}, status=400
            )

        # Extract system data from JSON
        username = data.get("username")
        hostname = data.get("hostname")
        operating_system = data.get("operating_system")
        operating_system_version = data.get("operating_system_version")

        # Create or update SystemData instance
        system_data, created = SystemData.objects.get_or_create(token=token)
        system_data.username = username
        system_data.hostname = hostname
        system_data.operating_system = operating_system
        system_data.operating_system_version = operating_system_version
        system_data.save()

        print("\nSending success response...")
        return JsonResponse(
            {
                "status": "success",
                "message": "System data stored successfully.",
                "data_id": system_data.id,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON data."}, status=400
        )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"}, status=500
        )


def set_notification(message, type):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    read = False

    notification = Notifications.objects.create(
        timestamp=timestamp,
        message=message,
        type=type,
        read=read,
    )
    notification.save()


def reports_view(request):
    tokens = APIToken.objects.all()

    token_details = []

    for token in tokens:

        system_data = SystemData.objects.filter(token=token).first()

        token_detail = {
            "token": token.token,
            "system_data": system_data,
            "generate_report": f"/api/generate_report/{token.token}/",
        }

        token_details.append(token_detail)

    print(token_detail)
    return render(request, "report.html", {"tokens": token_details})


def generate_reports(request,token):
    tokens = APIToken.objects.all()

    token_details = []

    for token in tokens:

        system_data = SystemData.objects.filter(token=token).first()

        token_detail = {
            "token": token.token,
            "system_data": system_data,
            "generate_report": f"/api/generate_report/{token.token}/",
        }

        token_details.append(token_detail)

    return render(request, "generate_report.html", {"tokens": token_details})


def terminal_view(request):
    tokens = APIToken.objects.all()

    token_details = []

    for token in tokens:

        system_data = SystemData.objects.filter(token=token).first()

        token_detail = {
            "token": token.token,
            "system_data": system_data,
            "generate_terminal": f"/api/generate_terminal/{token.token}/",
        }

        token_details.append(token_detail)

    return render(request, "terminal.html", {"tokens": token_details})


@csrf_exempt
def generate_terminal(request, token):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]

        commands_collection = db["myapp_command"]
        system_data_collection = db["myapp_systemdata"]
        cpu_data_collection = db["myapp_cpuinfo"]
        ram_data_collection = db["myapp_raminfo"]
        disk_data_collection = db["myapp_diskinfo"]

        system_data = system_data_collection.find_one({"token_id": token})
        cpu_data = list(cpu_data_collection.find({"token_id": token}, sort=[("_id", -1)]))
        ram_data = list(ram_data_collection.find({"token_id": token}, sort=[("_id", -1)]))
        disk_data = list(disk_data_collection.find({"token_id": token}, sort=[("_id", -1)]))

        latest_cpu_data = cpu_data[0] if cpu_data else {}
        latest_ram_data = ram_data[0] if ram_data else {}
        latest_disk_data = disk_data[0] if disk_data else {}

        if request.method == 'POST':
            command = request.POST.get('command')
            if command:

                last_command = commands_collection.find_one({"token_id": token}, sort=[("_id", -1)])
                
                command_id = last_command["id"] + 1 if last_command else 1

                command_entry = {
                    "id": command_id,
                    "token_id": token,
                    "command": command,
                    "executed": False,
                    "response": {}
                }

                commands_collection.insert_one(command_entry)

            return redirect('generate_terminal', token=token)
        
        commands_data = list(commands_collection.find({"token_id": token}))

        return render(request, 'generate_terminal.html', {
            'token': token,
            'commands': commands_data,
            'system_data': system_data,
            "cpu_percent": latest_cpu_data.get("cpu_percent", ""),
            "percent_memory": latest_ram_data.get("percent_memory", ""),
            "percent_disk": latest_disk_data.get("percent_disk", ""),
        })

    except Exception as e:
        return render(request, 'generate_terminal.html', {"error_message": str(e)})

@csrf_exempt
@require_POST
def send_executed_commands(request, token):
    try:
        data = json.loads(request.body)

        # Validate the data
        if not isinstance(data, list):
            return JsonResponse({"status": "error", "message": "Invalid data format"}, status=400)
        
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        commands_collection = db["myapp_command"]

        existing_commands = list(commands_collection.find({"token_id": token}))
        if not existing_commands:
            return JsonResponse({"status": "error", "message": "No commands found for the specified token"}, status=404)
        
        for command_update in data:
            command_id = command_update.get("_id")
            if command_id is None:
                continue
            
            command_object_id = ObjectId(command_id)

            for existing_command in existing_commands:
                if existing_command.get("_id") == command_object_id:
                    commands_collection.update_one(
                        {"_id": command_object_id},
                        {"$set": {"executed": True, "response": command_update.get("response")}},
                    )
                    break
        return JsonResponse({"status": "success", "message": "Executed commands updated successfully"})
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
def check_issued_commands(request, token):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        commands_collection = db["myapp_command"]

        # Fetch all commands for the specified token
        commands = list(commands_collection.find({"token_id": token}))

        logging.debug(f"Commands for token {token}: {commands}")

        unexecuted_commands = []

        if commands:
            for command_info in commands:
                if command_info and not command_info.get("executed", True):
                    command_info["_id"] = str(command_info["_id"])
                    unexecuted_commands.append(command_info)
        
        logging.debug(f"Unexecuted commands for token {token}: {unexecuted_commands}")
        
        return JsonResponse(unexecuted_commands, safe=False)
    
    except Exception as e:
        logging.error(f"Error in check_issued_commands: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
@require_POST
def store_ram_data(request):
    try:
        print("\nReceived request to store RAM data....")

        data = json.loads(request.body)
        token_value = data.get("token")

        if not token_value:
            print("\nToken is required. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Token is required"}, status=400
            )
        
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            print("\nInvalid token. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Invalid token"}, status=400
            )
        
        ram_data = data.get("data")
        if not ram_data:
            print("\nRAM data is missing. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "RAM data is missing"}, status=400
            )
        
        # Extract RAM information from the data
        total_memory = data.get("total_memory")
        available_memory = ram_data.get("available_memory")
        used_memory = ram_data.get("used_memory")
        free_memory = ram_data.get("free_memory")
        percent_memory = ram_data.get("percent_memory")
        total_swap = ram_data.get("total_swap")
        used_swap = ram_data.get("used_swap")
        free_swap = ram_data.get("free_swap")
        percent_swap = ram_data.get("percent_swap")

        timestamp_str = ram_data.get("timestamp")
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        timestamp_aware = timezone.make_aware(
            timestamp, timezone.get_current_timezone()
        )

        ram_info = RamInfo.objects.create(
            token=token,
            total_memory=total_memory,
            timestamp=timestamp_aware,
            available_memory=available_memory,
            used_memory=used_memory,
            free_memory=free_memory,
            percent_memory=percent_memory,
            total_swap=total_swap,
            used_swap=used_swap,
            free_swap=free_swap,
            percent_swap=percent_swap,
        )

        print("\nCreated new RAM data:", ram_info)
        response_data = {
            "status": "success",
            "message": "New RAM data stored successfully",
            "data_id": ram_info.id,
        }

        print("\nSending success response...")
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        print("\nInvalid JSON data. Sending error response...")
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON data"}, status=400
        )
    
    except Exception as e:
        print(f"An error occurred: {str(e)}. Sending error response...")
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"}, status=500
        )

@csrf_exempt
@require_POST
def store_disk_data(request):
    try:
        print("\nReceived request to store disk data...")

        data = json.loads(request.body)
        token_value = data.get("token")

        if not token_value:
            print("\nToken is required. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Token is required"}, status=400
            )
        
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            print("\nInvalid token. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Invalid token"}, status=400
            )
        
        disk_data = data.get("data")
        if not disk_data:
            print("\nDisk data is missing. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Disk data is missing"}, status=400
            )
        
        # Extract disk information from the data
        total_disk = data.get("total_disk")
        used_disk = disk_data.get("used_disk")
        free_disk = disk_data.get("free_disk")
        percent_disk = disk_data.get("percent_disk")

        timestamp_str = disk_data.get("timestamp")
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        timestamp_aware = timezone.make_aware(
            timestamp, timezone.get_current_timezone()
        )

        disk_info = DiskInfo.objects.create(
            token=token,
            total_disk=total_disk,
            timestamp=timestamp_aware,
            used_disk=used_disk,
            free_disk=free_disk,
            percent_disk=percent_disk,
        )

        print("\nCreated new disk data:", disk_info)
        response_data = {
            "status": "success",
            "message": "New disk data stored successfully",
            "data_id": disk_info.id,
        }

        print("\nSending success response...")
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        print("\nInvalid JSON data. Sending error response...")
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON data"}, status=400
        )
    
    except Exception as e:
        print(f"An error occurred: {str(e)}. Sending error response...")
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"}, status=500
        )

def ram_info_page(request, token):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["myapp_raminfo"]

        # Fetch all RAM data for the specified token
        ram_data = list(collection.find({"token_id": token}, sort=[("_id", -1)]))
        system_data = SystemData.objects.filter(token=token).first()

        if ram_data:
            # Get the last fetched RAM data
            last_ram_data = ram_data[0]

            hostname = system_data.hostname
            username = system_data.username
            operating_system = system_data.operating_system

            context = {
                "timestamp": last_ram_data.get("timestamp"),
                "total_memory": last_ram_data.get("total_memory"),
                "available_memory": last_ram_data.get("available_memory"),
                "used_memory": last_ram_data.get("used_memory"),
                "free_memory": last_ram_data.get("free_memory"),
                "percent_memory": last_ram_data.get("percent_memory"),
                "total_swap": last_ram_data.get("total_swap"),
                "used_swap": last_ram_data.get("used_swap"),
                "free_swap": last_ram_data.get("free_swap"),
                "percent_swap": last_ram_data.get("percent_swap"),
                "hostname": hostname,
                "username": username,
                "operating_system": operating_system,
            }

            return render(request, "ram_info.html", context)
        else:
            return render(
                request,
                "ram_info.html",
                {"error_message": f"No data found for token: {token}"},
            )
    except Exception as e:
        return render(
            request,
            "ram_info.html",
            {"error_message": f"An error occurred: {str(e)}"},
        )
>>>>>>> Stashed changes
