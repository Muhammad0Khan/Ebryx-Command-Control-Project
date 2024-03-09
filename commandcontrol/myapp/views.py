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

        return JsonResponse({"exists": token_exists})

    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred while checking the token: {str(e)}"},
            status=500,
        )


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
    # Assuming you have a Firebase Admin instance initialized

    # Reference to the 'tokens' collection
    tokens_ref = db.reference("tokens")
    # Reference to the 'status' collection
    status_ref = db.reference("status")

    # Retrieve token data
    tokens_data = tokens_ref.order_by_child("token").get()

    # Retrieve status data
    status_data = status_ref.order_by_child("token").get()
    # print(status_data)

    # Create a list of tokens with details, including matching status
    tokens = []
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

        # Create a dictionary with token details and status
        token_details = {
            "token": token["token"],
            "details_url": f'/token-details/{token["token"]}/',
            "cpu_info": f'/api/cpu_info/{token["token"]}/',
            "status": status.get("status", "N/A"),  # Use 'N/A' if no status found
        }
        print(token_details)

        tokens.append(token_details)

    return render(request, "dashboard.html", {"tokens": tokens})


def token_details_view(request, token):
    # Fetch data from the installed_apps collection for the specific token
    apps_ref = db.reference("installed_apps").child(token)
    cpu_data_ref = db.reference("cpu_data").child(token)
    username = cpu_data_ref.get().get("data", [])[-1].get("username", "")
    token_data = apps_ref.get()

    if token_data:
        installed_apps_data = token_data.get("data", [])
    else:
        installed_apps_data = []

    return render(
        request,
        "token_details.html",
        {"username": username, "installed_apps": installed_apps_data},
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


def set_status_offline(token, delay=30):
    try:
        # Find the APIToken entry for the given token
        token_entry = APIToken.objects.filter(token=token).first()

        # Update the status to 'offline' if a matching token is found
        if token_entry:
            time.sleep(delay)
            token_entry.status = "offline"
            token_entry.save()
            print(f"Status updated to 'offline' for token: {token}")
        else:
            print(f"No matching token found for status update: {token}")

    except Exception as e:
        print(f"Error updating status for token: {token}: {e}")


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
        print("Received request to store CPU data...")

        # Parse request body
        data = json.loads(request.body)
        print("Parsed request body:", data)

        token_value = data.get("token")
        print("Extracted token from data:", token_value)

        if not token_value:
            print("Token is required. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Token is required"}, status=400
            )

        # Check if the token exists
        token = APIToken.objects.filter(token=token_value).first()
        if not token:
            print("Invalid token. Sending error response...")
            return JsonResponse(
                {"status": "error", "message": "Invalid token"}, status=400
            )

        cpu_data = data.get("data")
        if not cpu_data:
            print("CPU data is missing. Sending error response...")
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
        timestamp_aware = timezone.make_aware(timestamp, timezone.get_current_timezone())

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
            print("Created new CPU data:", cpu_info)
            response_data = {
                "status": "success",
                "message": "New CPU data stored successfully",
                "data_id": cpu_info.id,
            }
        else:
            print("Updated existing CPU data:", cpu_info)
            response_data = {
                "status": "success",
                "message": "CPU data updated successfully",
                "data_id": cpu_info.id,
            }

        print("Sending success response...")
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        print("Invalid JSON data. Sending error response...")
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
        cpu_data_ref = db.reference(f"cpu_data/{token}")

        # Fetch the CPU data for the specified token
        cpu_data = cpu_data_ref.get()

        if cpu_data:
            # Get the last data section (assuming it's a list of dictionaries)
            last_data_section = cpu_data.get("data", [])[-1]

            context = {
                "system_name": last_data_section.get("system_name", ""),
                "hostname": last_data_section.get("hostname", ""),
                "username": last_data_section.get("username", ""),
                "threads": last_data_section.get("threads", ""),
                "cpu_count": last_data_section.get("cpu_count", ""),
                "cpu_usage": last_data_section.get("data", {}).get("cpu_usage", ""),
                "cpu_frequency": last_data_section.get("data", {}).get(
                    "cpu_frequency", ""
                ),
                "per_cpu_percent": last_data_section.get("data", {}).get(
                    "per_cpu_percent", ""
                ),
                "timestamp": last_data_section.get("data", {}).get("timestamp", ""),
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
            request, "cpu_info.html", {"error_message": f"An error occurred: {str(e)}"}
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
