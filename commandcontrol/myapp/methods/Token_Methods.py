from django.http import JsonResponse
from firebase_admin import db
import time



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