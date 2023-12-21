from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from myapp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from datetime import datetime
import subprocess,json,time, psutil
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
from .models import FirebaseUser
from django.views.decorators.http import require_POST




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

    ref_create_online_status= db.reference('status')
    ref_create_online_status.push().set({'token': token, 'status':"offline"})

    # Return the token in the API response
    return Response({'token': token})



def check_token(request, token):
    try:
        # Reference to the Firebase Realtime Database node where you store tokens
        tokens_ref = db.reference('/tokens')

        # Query the database to check if the token exists
        query = tokens_ref.order_by_child('token').equal_to(token).get()
        update_token_status(token)
        set_status_offline(token, delay=30)

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


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create a new FirebaseUser instance and save it to Firebase RTDB
            user = FirebaseUser(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            user.save_to_firebase()
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = SignupForm()

        return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Fetch user data from Firebase based on the email
            user_data = db.reference('/users').child(email.replace('.', ',')).get()
            print(user_data)

            if user_data:
                # Authenticate user against provided credentials
                user = authenticate(request, email=email, password=password)
                
                if user:
                    login(request, user)
                    print(f'Sign-in successful for user: {user.email}')
                    return redirect('home')  # Redirect to the home page after successful sign-in
                else:
                    # Authentication failed
                    # You may want to add an error message here
                    print(f'Authentication failed for user: {email}')
            else:
                # User data not found
                # You may want to add an error message here
                print(f'User not found for email: {email}')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

def dashboard_view(request):
    # Assuming you have a Firebase Admin instance initialized

    # Reference to the 'tokens' collection
    tokens_ref = db.reference('tokens')
    # Reference to the 'status' collection
    status_ref = db.reference('status')

    # Retrieve token data
    tokens_data = tokens_ref.order_by_child('token').get()

    # Retrieve status data
    status_data = status_ref.order_by_child('token').get()

    # Create a list of tokens with details, including matching status
    tokens = []
    for token_key, token in tokens_data.items():
        # Check if there is a corresponding status for the token
        status_key = next((key for key, value in status_data.items() if value['token'] == token['token']), None)
        status = status_data.get(status_key, {}) if status_key else {}

        # Create a dictionary with token details and status
        token_details = {
            'token': token['token'],
            'details_url': f'/token-details/{token["token"]}/',
            'status': status.get('status', 'N/A'),  # Use 'N/A' if no status found
        }

        tokens.append(token_details)

    return render(request, 'dashboard.html', {'tokens': tokens})

def token_details_view(request, token):
    # Fetch data from the installed_apps collection for the specific token
    apps_ref = db.reference('installed_apps').child(token)
    token_data = apps_ref.get()

    if token_data:
        installed_apps_data = token_data.get('data', [])
    else:
        installed_apps_data = []

    return render(request, 'token_details.html', {'token': token, 'installed_apps': installed_apps_data})


def update_token_status(token):
    print('function called ')
    # Reference to the 'status' collection
    status_ref = db.reference('status')

    # Find the status entry for the given token
    status_data = status_ref.order_by_child('token').equal_to(token).get()

    print (status_data)

    # Update the status to 'online' if a matching status is found
    if status_data:
        status_key = list(status_data.keys())[0]
        status_ref.child(status_key).update({'status': 'online'})
        print(f"Status updated to 'online' for token: {token}")
    else:
        print(f"No matching status found for token: {token}")



def set_status_offline(token, delay=30):
    # Reference to the 'status' collection
    status_ref = db.reference('status')

    # Find the status entry for the given token
    status_data = status_ref.order_by_child('token').equal_to(token).get()

    # Update the status to 'offline' after a delay if a matching status is found
    if status_data:
        status_key = list(status_data.keys())[0]
        
        # Sleep for the specified delay in seconds
        time.sleep(delay)

        # Update the status to 'offline'
        status_ref.child(status_key).update({'status': 'offline'})
        print(f"Status updated to 'offline' for token: {token}")
    else:
        print(f"No matching status found for token: {token}")


@api_view(['DELETE'])
def delete_token(request, token):
    try:
        # Reference to the 'status' collection
        status_ref = db.reference('status')

        # Find the status entry for the given token
        status_data = status_ref.order_by_child('token').equal_to(token).get()

        # Delete the token entry if a matching status is found
        if status_data:
            status_key = list(status_data.keys())[0]
            status_ref.child(status_key).delete()
            return Response({'success': True, 'message': f'Token {token} deleted successfully'})
        else:
            return Response({'success': False, 'message': f'No matching status found for token: {token}'})
    except Exception as e:
        return Response({'success': False, 'error': str(e)})
    

@csrf_exempt
@require_POST
def store_cpu_data(request):
    try:
        data = json.loads(request.body)
        token = data.get('token')

        if not token:
            response_data = {
                'status': 'error',
                'message': 'Token is required in the JSON data.',
            }
            return JsonResponse(response_data, status=400)

        # Assuming 'cpu_data' is the reference to the desired location in your RTDB
        cpu_data_ref = db.reference(f'cpu_data/{token}')

        # Fetch the existing data array or initialize an empty array
        existing_data = cpu_data_ref.child('data').get() or []

        # Append the new data section to the array
        existing_data.append(data)

        # Update the RTDB with the new data array
        cpu_data_ref.update({'data': existing_data})

        response_data = {
            'status': 'success',
            'message': 'CPU data stored successfully',
            'data_id': len(existing_data) - 1,  # Index of the last appended data section
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        response_data = {
            'status': 'error',
            'message': 'Invalid JSON data',
        }
        return JsonResponse(response_data, status=400)

    except Exception as e:
        response_data = {
            'status': 'error',
            'message': f'An error occurred: {str(e)}',
        }
        return JsonResponse(response_data, status=500)


def cpu_info_page(request, token):
    try:
        cpu_data_ref = db.reference(f'cpu_data/{token}')

        # Fetch the CPU data for the specified token
        cpu_data = cpu_data_ref.get()

        if cpu_data:
            # Get the last data section (assuming it's a list of dictionaries)
            last_data_section = cpu_data.get('data', [])[-1]

            context = {
                'system_name': last_data_section.get('system_name', ''),
                'hostname': last_data_section.get('hostname', ''),
                'threads': last_data_section.get('threads', ''),
                'cpu_count': last_data_section.get('cpu_count', ''),
                'cpu_usage': last_data_section.get('data', {}).get('cpu_usage', ''),
                'cpu_frequency': last_data_section.get('data', {}).get('cpu_frequency', ''),
                'per_cpu_percent': last_data_section.get('data', {}).get('per_cpu_percent', ''),
                'timestamp': last_data_section.get('data', {}).get('timestamp', ''),
                
            }

            print (context)
            return render(request, 'cpu_info.html', context)
        else:
            return render(request, 'cpu_info.html', {'error_message': f'No data found for token: {token}'})
    except Exception as e:
        return render(request, 'cpu_info.html', {'error_message': f'An error occurred: {str(e)}'})