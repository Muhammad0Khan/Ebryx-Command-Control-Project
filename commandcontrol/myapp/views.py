from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse, HttpResponseServerError
from myapp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from datetime import datetime
import subprocess, json, time, psutil
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

    # Store the token in Firestore
    ref = db.reference("tokens")
    ref.push().set({"token": token})

    ref_create_online_status = db.reference("status")
    ref_create_online_status.push().set({"token": token, "status": "offline"})

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
    token_data = apps_ref.get()

    if token_data:
        installed_apps_data = token_data.get("data", [])
    else:
        installed_apps_data = []

    return render(
        request,
        "token_details.html",
        {"token": token, "installed_apps": installed_apps_data},
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

        # Fetch the network data for the specified token
        network_data = network_data_ref.get()

        if network_data:
            # Get the last data section (assuming it's a list of dictionaries)
            last_data_section = network_data.get("data", [])[-1]

            # Convert network_data to a format suitable for JSON serialization
            network_info_serialized = [
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

            context = {
                "token": token,
                "network_info": network_info_serialized,
                "last_data_section": last_data_section,
            }

            if request.headers.get("Content-Type") == "application/json":
                # Return JSON response for API requests
                response_data = {
                    "success": True,
                    "token": token,
                    "network_info": network_info_serialized,
                    "last_data_section": last_data_section,
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
