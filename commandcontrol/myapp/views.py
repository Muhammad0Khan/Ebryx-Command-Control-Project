from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from myapp.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import logout
from datetime import datetime
import subprocess,json,time, psutil
from firebase_admin import db
from .firebase_init import initialize_firebase
from .utils import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from .models import *
from django.shortcuts import render, redirect
from .serializers import InstalledAppSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView




initialize_firebase()


@csrf_exempt
def cpu_info_view(request):
    # Fetch the latest CPU information from the database
    latest_cpu_info = CPUInfo.objects.latest("timestamp")

    # Prepare data to pass to the template
    context = {
        "timestamp": timezone.localtime(latest_cpu_info.timestamp),
        "cpu_count": latest_cpu_info.cpu_count,
        "cpu_percent": latest_cpu_info.cpu_percent,
        "cpu_freq_value": latest_cpu_info.cpu_freq_value,
        "threads": latest_cpu_info.threads,
        "per_cpu_percent": latest_cpu_info.per_cpu_percent,
    }

    # Render the template with the data
    return render(request, "cpu_info.html", context)


@login_required
def profile_view(request):
    user = request.user
    # Get the IP address and PC name of the remote client
    remote_ip = request.META.get("REMOTE_ADDR", "")
    # Used if fetching the PC name for Windows clients
    pc_name_windows = request.META.get("COMPUTERNAME", "")

    # Used if fetching the PC name for Mac clients
    try:
        pc_name_mac = subprocess.check_output(
            ["scutil", "--get", "LocalHostName"], universal_newlines=True
        ).strip()
    except subprocess.CalledProcessError:
        pc_name_mac = ""

    # Determine the PC name based on the OS of the remote client
    pc_name = pc_name_windows if pc_name_windows else pc_name_mac

    # Get CPU Information of the remote client
    cpu_info = psutil.cpu_stats()
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=None)
    try:
        cpu_freq = psutil.cpu_freq().current
    except FileNotFoundError:
        cpu_freq = -1
    threads = psutil.cpu_count(logical=False)
    per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Save or update CPU information of the remote client in the database
    remote_cpu_info, created = RemoteCPUInfo.objects.update_or_create(
        user=user,
        remote_ip=remote_ip,
        defaults={
            "pc_name": pc_name,
            "timestamp": timestamp,
            "cpu_count": cpu_count,
            "cpu_percent": cpu_percent,
            "cpu_freq_value": cpu_freq,
            "threads": threads,
            "per_cpu_percent": per_cpu_percent,
            "status": "Online",
        },
    )

    # save the same information in firebase
    firebase_ref = db.reference("remote_cpu_information")
    firebase_ref.push(
        {
            "user": user.username,
            "remote_ip": remote_ip,
            "pc_name": pc_name,
            "timestamp": timestamp,
            "cpu_count": cpu_count,
            "cpu_percent": cpu_percent,
            "cpu_freq_value": cpu_freq,
            "threads": threads,
            "per_cpu_percent": per_cpu_percent,
            "status": "Online",
        }
    )

    # Prepare data to pass to the template
    context = {
        "user": user,
        "status": "Online",
        "remote_ip": remote_ip,
        "pc_name": pc_name,
        "timestamp": timestamp,
        "cpu_count": cpu_count,
        "cpu_percent": cpu_percent,
        "cpu_freq_value": cpu_freq,
        "threads": threads,
        "per_cpu_percent": per_cpu_percent,
    }

    # Render the template with the data
    return render(request, "profile.html", context)


@login_required
def logout_view(request):
    user = request.user

    logout(request)

    if user.is_authenticated:
        RemoteCPUInfo.objects.filter(user=user).update(status="Offline")

        # update the status in firebase
        firebase_ref = db.reference("remote_cpu_information")
        user_info = firebase_ref.order_by_child("timestamp").limit_to_last(1).get()

        if user_info:
            key = list(user_info.keys())[0]
            firebase_ref.child(key).update({"status": "Offline"})

    return redirect("login")


@csrf_exempt
def remote_cpu_info_api(request):
    if request.method == "POST":
        remote_ip = request.META.get("REMOTE_ADDR", "")
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"})

        user, created = User.objects.get_or_create(username=payload.get("username"))

        timestamp_str = payload.get("timestamp")
        parsed_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        aware_timestamp = timezone.make_aware(parsed_timestamp, timezone=timezone.utc)

        payload["timestamp"] = timezone.localtime(aware_timestamp)
        payload["user"] = user
        payload["remote_ip"] = remote_ip
        payload["cpu_count"] = payload.get("cpu_count")
        payload["cpu_percent"] = payload.get("cpu_percent")
        payload["cpu_freq_value"] = payload.get("cpu_freq_value")
        payload["threads"] = payload.get("threads")
        payload["per_cpu_percent"] = payload.get("per_cpu_percent")

        remote_cpu_info, created = RemoteCPUInfo.objects.update_or_create(
            remote_ip=remote_ip,
            defaults=payload,
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})

def installed_apps(request):
    installed_apps_last_12_hours = get_installed_apps_last_12_hours()
    return render(request, 'installed_apps.html', {'installed_apps': installed_apps_last_12_hours})


def running_processes(request):
    running_processes_data = get_running_processes()
    return render(request, 'running_processes.html', {'running_processes': running_processes_data})


# added apis here 
@api_view(['GET'])
def generate_token(request):
    # Generate a unique token
    token = get_random_string(length=40)

    # Store the token in Firestore
    ref = db.reference('tokens')
    ref.push().set({'token': token})

    # Return the token in the API response
    return Response({'token': token})



def check_token(request, token):
    try:
        # Reference to the Firebase Realtime Database node where you store tokens
        tokens_ref = db.reference('/tokens')

        # Query the database to check if the token exists
        query = tokens_ref.order_by_child('token').equal_to(token).get()

        if query:
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
def save_firebase_token(token_value):
    APIToken.objects.create(token_value=token_value)

class InstalledAppAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InstalledAppSerializer(data=request.data)
        if serializer.is_valid():
            # Save to the Firebase Realtime Database
            token = serializer.validated_data.get('token')
            firebase_ref = db.reference(f'/installed_apps/{token}')
            firebase_ref.set(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
