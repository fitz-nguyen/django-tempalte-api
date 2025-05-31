from allauth.account.models import EmailAddress, EmailConfirmation

from apps.users.choices import SALE
from apps.users.models import User
from apps.users.services import send_mail
from apps.users_auth.exceptions import EmailIsNotValidException, UserIsNotActiveException


def resend_confirmation_email(username: str = None, email: str = None):
    user = None
    if username:
        user = User.objects.filter(username__iexact=username).first()
    elif email:
        user = User.objects.filter(email=email).first()
    if not user:
        raise EmailIsNotValidException("There is not user exist with this email.")
    email_address = EmailAddress.objects.filter(user=user, email=user.email).first()
    if not email_address:
        email_address = EmailAddress.objects.create(user=user, email=user.email, primary=True)
    # Delete expired token
    EmailConfirmation.objects.delete_expired_confirmations()
    EmailConfirmation.objects.all_valid().filter(email_address=email_address).delete()
    email_confirmation = EmailConfirmation.create(email_address=email_address)
    # Send
    email_confirmation.send(signup=True)


def forgot_username(to_email: str, role: str = ""):
    if not to_email:
        return
    else:
        to_email = to_email.lower()

    try:
        if role == SALE:
            user = User.objects.get(email__iexact=to_email, role=SALE)
        else:
            user = User.objects.filter(email__iexact=to_email).exclude(role=SALE).first()
            if not user:
                return
        if not user.is_active:
            raise UserIsNotActiveException()

    except User.DoesNotExist:
        return

    context = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    text_email_template_name = "account/email/forgot_username.txt"
    html_email_template_name = "account/email/forgot_username.html"
    subject_template_name = "account/email/forgot_username_subject.txt"

    send_mail(
        subject_template_name,
        text_email_template_name,
        context,
        to_email,
        html_email_template_name=html_email_template_name,
    )


def send_under_review_mail(to_email: str):
    if not to_email:
        return
    else:
        to_email = to_email.lower()

    try:
        user = User.objects.filter(email__iexact=to_email).first()
        if not user:
            return

    except User.DoesNotExist:
        return

    context = {
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    text_email_template_name = "account/under_review/under_review.txt"
    html_email_template_name = "account/under_review/under_review.html"
    subject_template_name = "account/under_review/under_review_subject.txt"

    send_mail(
        subject_template_name,
        text_email_template_name,
        context,
        to_email,
        html_email_template_name=html_email_template_name,
    )
