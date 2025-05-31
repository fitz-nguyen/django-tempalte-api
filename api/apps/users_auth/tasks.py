from apps.core.celery import app
from apps.users_auth.services import resend_confirmation_email


@app.task(autoretry_for=(Exception,), max_retries=2)
def send_confirm_email_task(email: str, **kwargs):
    resend_confirmation_email(email=email)
