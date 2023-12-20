from django.apps import AppConfig
import firebase_admin


class MyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        # Check if the Firebase app is already initialized
        if not firebase_admin._apps:
            # Initialize the Firebase app
            firebase_admin.initialize_app()
            print("Firebase app initialized successfully.")
        else:
            print("Firebase app already initialized")
