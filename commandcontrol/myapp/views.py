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
@csrf_exempt
def check_token(request, token):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["myapp_apitoken"]

        # Check if the token exists in MongoDB
        token_exists = collection.find_one({"token": token}) is not None

        update_token_status(token)

        return JsonResponse({"exists": token_exists})

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
        return JsonResponse({"exists": user_exists})

    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred while checking the username: {str(e)}"},
            status=500,
        )


def update_token_status(token):
    try:
        # Find the APIToken entry for the given token
        token_entry = APIToken.objects.filter(token=token).first()

        # Update the status to 'online' if a matching token is found
        if token_entry:
            token_entry.status = "online"
            token_entry.last_active = timezone.now()
            token_entry.save()
            print(f"Status updated to 'online' for token: {token}")
        else:
            print(f"No matching token found for status update: {token}")

    except Exception as e:
        print(f"Error updating status for token: {token}: {e}")


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


def logout_view(request):
    logout(request)
    return redirect("login")


# Installed Apps Storage and Viewing
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

        if cpu_data:
            # Get the last fetched CPU data
            last_cpu_data = cpu_data[0]
            percent_per_cpu_values = last_cpu_data.get("percent_per_cpu", [])

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


# Network Stats Storage and Viewing
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


def network_info_page(request, token):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["commandcontrol"]
        collection = db["myapp_networkstats"]

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
