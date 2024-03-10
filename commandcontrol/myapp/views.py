from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from myapp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
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
from .forms import LoginForm
from django.views.decorators.http import require_POST
import pyrebase
from .firebase_init import initialize_firebase
from pymongo import MongoClient
from datetime import datetime

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
    logout(request)
    return redirect("login")


# added apis here
@api_view(["GET"])
@csrf_exempt
def generate_token(request):
    try:
        # Generate a random token
        token = get_random_string(length=40)

        # Store the token in MongoDB
        APIToken.objects.create(token=token)

        # Update the token status to 'online'
        update_token_status(token)

        # Return the token in the response
        return JsonResponse({"token": token})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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


@login_required
def dashboard_view(request):
    # Retrieve token data from MongoDB
    tokens_data = APIToken.objects.all()

    # Create a list of tokens with details
    tokens = []
    for token in tokens_data:
        # Get the status of the token
        status = token.status
        # Get the last active time of the token
        last_active = token.last_active
        # Create a dictionary with token details, status and last active
        token_details = {
            "token": token.token,
            "details_url": f"/token-details/{token.token}/",
            "cpu_info": f"/api/cpu_info/{token.token}/",
            "network_info": f"/api/network_info/{token.token}/",
            "status": status if status else "offline",
            "last_active": last_active.strftime("%Y-%m-%d %H:%M:%S"),
        }

        tokens.append(token_details)

    return render(request, "dashboard.html", {"tokens": tokens})


def token_details_view(request, token):
    # fetch installed apps data for the specific token
    installed_apps_data = InstalledApp.objects.filter(token=token).values_list(
        "data", flat=True
    )

    # Convert the QuerySet to a list
    installed_apps_data = list(installed_apps_data)
    print(installed_apps_data)

    return render(
        request,
        "token_details.html",
        {"token": token, "installed_apps_data": installed_apps_data},
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

        # Delete all matching token entries
        if status_data:
            for status_key in status_data.keys():
                status_ref.child(status_key).delete()

        if cpu_data:
            cpu_ref.child(token).delete()

        if network_data:
            network_ref.child(token).delete()

        if user_token_data:
            for token_key in user_token_data.keys():
                user_token_ref.child(token_key).delete()

        return Response({"success": True, "message": "Token deleted successfully"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


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

        # Create or update CPUInfo object
        cpu_info, created = CPUInfo.objects.update_or_create(
            token=token,
            defaults={
                "timestamp": timestamp_aware,
                "cpu_count": cpu_count,
                "threads": threads,
                "cpu_percent": cpu_percent,
                "cpu_freq_value": cpu_freq_value,
                "percent_per_cpu": percent_per_cpu,
            },
        )

        if created:
            print("\nCreated new CPU data:", cpu_info)
            response_data = {
                "status": "success",
                "message": "New CPU data stored successfully",
                "data_id": cpu_info.id,
            }
        else:
            print("\nUpdated existing CPU data:", cpu_info)
            response_data = {
                "status": "success",
                "message": "CPU data updated successfully",
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
        cpu_data = collection.find_one({"token_id": token}, sort=[("_id", -1)])

        if cpu_data:
            context = {
                "timestamp": cpu_data.get("timestamp"),
                "cpu_count": cpu_data.get("cpu_count"),
                "threads": cpu_data.get("threads"),
                "cpu_percent": cpu_data.get("cpu_percent"),
                "cpu_freq_value": cpu_data.get("cpu_freq_value"),
                "percent_per_cpu": cpu_data.get("percent_per_cpu"),
            }
            print(context)
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


# /api/network_data
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

        network_data_list = data.get(
            "data", []
        )  # Fetch the 'data' key from the JSON payload
        if not network_data_list:
            response_data = {
                "status": "error",
                "message": "Network data is missing",
            }
            return JsonResponse(response_data, status=400)

        # Construct a dictionary to hold all interface data
        all_interface_data = {}
        for network_data in network_data_list:
            iface = network_data.get("iface")
            if not iface:
                print("Interface name is missing. Skipping...")
                continue

            # Add interface data to the dictionary
            all_interface_data[iface] = network_data.get("data", {})

        # Create or update the NetworkStats object with all interface data
        network_stats, created = NetworkStats.objects.update_or_create(
            token=token, defaults={"data": all_interface_data}
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
        # Assuming 'network_data' is the reference to the desired location in your Firebase
        network_data_ref = db.reference(f"network_data/{token}")
        cpu_data_ref = db.reference(f"cpu_data/{token}")

        # Fetch all network data for the specified token
        network_data = network_data_ref.get()

        if network_data:
            # Convert network_data to a format suitable for JSON serialization
            network_info_serialized = []

            for data_section in network_data.get("data", []):
                for entry in data_section.get("data", []):
                    network_info_serialized.append(
                        {
                            "iface": entry.get("iface", ""),
                            "data": {
                                "download": entry["data"].get("download", ""),
                                "total_upload": entry["data"].get("total_upload", ""),
                                "upload_speed": entry["data"].get("upload_speed", ""),
                                "download_speed": entry["data"].get(
                                    "download_speed", ""
                                ),
                            },
                        }
                    )

            last_data_section = network_data.get("data", [])[-1]
            last_data_serialized = [
                {
                    "iface": entry.get("iface", ""),
                    "data": {
                        "download": entry["data"].get("download", ""),
                        "total_upload": entry["data"].get("total_upload", ""),
                        "upload_speed": entry["data"].get("upload_speed", ""),
                        "download_speed": entry["data"].get("download_speed", ""),
                    },
                }
                for entry in last_data_section.get("data", [])
            ]

            username = cpu_data_ref.get().get("data", [])[-1].get("username", "")

            context = {
                "username": username,
                "network_info": network_info_serialized,
                "all_data_sections": network_data.get("data", []),
                "last_data_section": last_data_serialized,
            }

            if request.headers.get("Content-Type") == "application/json":
                # Return JSON response for API requests
                response_data = {
                    "success": True,
                    "username": username,
                    "network_info": network_info_serialized,
                    "all_data_sections": network_data.get("data", []),
                    "last_data_section": last_data_serialized,
                }
                return JsonResponse(response_data)
            else:
                # Render HTML template for regular requests
                return render(request, "network_info.html", context)

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
