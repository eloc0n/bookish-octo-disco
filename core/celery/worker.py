from config import celery_app


# Optional: for debugging
@celery_app.task(name="health_check")
def health_check():
    return "OK"
