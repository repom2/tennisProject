import uvicorn
import os
import django

# from tennisproject.asgi import application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tennisproject.settings")
django.setup()

# app = get_default_application()


if __name__ == "__main__":
    uvicorn.run(
        "tennisproject.asgi:application",
        host="0.0.0.0",  # nosec B104
    )  # Pass additional command line options as kwargs
