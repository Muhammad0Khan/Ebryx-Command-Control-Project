from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from myapp.models import CPUInfo
from myapp.models import RemoteCPUInfo
import json
import psutil


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


@csrf_exempt
def remote_cpu_info(request):
    # Get the IP address of the remote client
    remote_ip = request.META.get("REMOTE_ADDR", "")

    # Get CPU Information of the remote client
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=None)
    try:
        cpu_freq = psutil.cpu_freq().current
    except FileNotFoundError:
        cpu_freq = -1
    threads = psutil.cpu_count(logical=False)
    per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)

    # Save or update CPU information of the remote client in the database
    remote_cpu_info, created = RemoteCPUInfo.objects.update_or_create(
        remote_ip=remote_ip,
        defaults={
            "cpu_count": cpu_count,
            "cpu_percent": cpu_percent,
            "cpu_freq_value": cpu_freq,
            "threads": threads,
            "per_cpu_percent": per_cpu_percent,
        },
    )

    # Prepare data to pass to the template
    context = {
        "remote_ip": remote_ip,
        "cpu_count": cpu_count,
        "cpu_percent": cpu_percent,
        "cpu_freq_value": cpu_freq,
        "threads": threads,
        "per_cpu_percent": per_cpu_percent,
    }

    # Render the template with the data
    return render(request, "remote_cpu_info.html", context)


@csrf_exempt
def remote_cpu_info_api(request):
    if request.method == "POST":
        remote_ip = request.META.get("REMOTE_ADDR", "")
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"})

        # Save or update CPU information of the remote client in the database
        remote_cpu_info, created = RemoteCPUInfo.objects.update_or_create(
            remote_ip=remote_ip,
            defaults={
                "cpu_count": payload.get("cpu_count"),
                "cpu_percent": payload.get("cpu_percent"),
                "cpu_freq_value": payload.get("cpu_freq_value"),
                "threads": payload.get("threads"),
                "per_cpu_percent": payload.get("per_cpu_percent"),
            },
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})
