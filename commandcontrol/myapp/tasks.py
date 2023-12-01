from celery import shared_task
from .cpu_info_script import save_cpu_info_to_firebase_and_server


@shared_task
def gather_cpu_info():
    save_cpu_info_to_firebase_and_server()
