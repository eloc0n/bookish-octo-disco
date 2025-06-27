from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", "rpc://")

celery_app = Celery(
    "fastapi_app", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL, include=[]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
