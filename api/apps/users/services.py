from typing import Dict

from allauth.account.models import EmailAddress
from apps.core.utils import get_media_url
from apps.systems.utils import SystemConfigCache
from apps.uploads.services.usercases import UploadFileService
from apps.users import choices
from apps.users.exceptions import (
    CompanyIsNotValidException,
    LogInException,
    MissedUsernameEmailPhoneException,
)
from apps.users.models import Company, SaleLog, User
from apps.users.signals import user_avatar_updated_signal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template import loader


def exists_user(username=None, email=None, phone=None):
    if not username and not email and not phone:
        raise MissedUsernameEmailPhoneException
    if username:
        queryset = User.objects.filter(username__iexact=username)
    elif email:
        queryset = User.objects.filter(email__iexact=email)
    else:
        queryset = User.objects.filter(phone__iexact=phone)
    count = queryset.count()
    return count > 0


def get_user(user_id: str) -> User:
    try:
        return User.objects.get(pk=user_id)
    except Exception:
        raise LogInException()


def update_user(instance: User, data: Dict, avatar: str):
    with transaction.atomic():
        # email = data.get("email", instance.email)
        # instance.email = email.lower()
        instance.first_name = data.get("first_name", instance.first_name)
        instance.last_name = data.get("last_name", instance.last_name)
        instance.display_name = f"{instance.first_name} {instance.last_name}"
        instance.notification = data.get("notification", instance.notification)
        # Update company contact information if company exists
        if instance.company:
            request_company = data.get("company", {})
            company: Company = instance.company
            if Company.objects.filter(business_name__iexact=request_company.get("business_name", "")).exists():
                raise CompanyIsNotValidException()
            company.business_name = request_company.get("business_name", company.business_name)
            company.business_address = request_company.get("business_address", company.business_address)
            company.region_served = request_company.get("region_served", company.region_served)
            company.contact_firstname = request_company.get("contact_fullname", company.contact_firstname)
            company.contact_lastname = request_company.get("contact_fullname", company.contact_lastname)
            company.contact_phone_number = request_company.get("contact_phone_number", company.contact_phone_number)
            company.contact_phone_country_code = request_company.get(
                "contact_phone_country_code", company.contact_phone_country_code
            )
            if company.contact_phone_number and company.contact_phone_country_code:
                company.contact_phone_e164 = company.contact_phone_country_code + company.contact_phone_number
            company.save()
        if avatar != instance.avatar:
            service = UploadFileService(instance)
            if instance.avatar:
                service.delete(instance.avatar)
            instance.avatar_thumb = None
            instance.avatar = avatar
            instance.save()
            service.mark_file_used(avatar)
            user_avatar_updated_signal.send(sender=User, user=instance)
        instance.save()
        return instance


def update_email_address(instance: User, email):
    if not email:
        return
    email_address = EmailAddress.objects.filter(user=instance).first()
    if email_address and email != email_address.email:
        email_address.email = email
        email_address.verified = True
        email_address.save()


def handle_avatar_when_sign_up(avatar: str):
    if avatar:
        services = UploadFileService(None)
        services.mark_file_used(avatar)


def send_mail(
    subject_template_name,
    email_template_name,
    context,
    to_email,
    from_email=None,
    extra_email_context=None,
    html_email_template_name=None,
):
    """
    Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = "".join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    if isinstance(to_email, list):
        to_email = to_email
    else:
        to_email = [to_email]

    email_message = EmailMultiAlternatives(subject, body, from_email, to_email)
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, "text/html")

    email_message.send()


def handle_post_save_user(instance_id: str):
    try:
        instance = User.objects.get(id=instance_id)
    except User.DoesNotExist:
        return

    if instance.status == choices.APPROVED:
        subject_template_name = "account/email/email_approve_demo_account_subject.txt"
        text_email_template_name = "account/email/email_approve_demo_account.txt"
        html_email_template_name = "account/email/email_approve_demo_account.html"
        email = instance.email
        login_link = f"{settings.FRONTEND_BASE_URL}/login/"
        context = {
            "email": email,
            "user": instance,
            "name": instance.name,
            "login_link": login_link,
            "footer_image_url": SystemConfigCache().email_footer_url,
        }
        send_mail(
            subject_template_name,
            text_email_template_name,
            context,
            email,
            html_email_template_name=html_email_template_name,
        )
        User.objects.filter(id=instance_id).update(is_sent_mail_approve_account=True, email_verified=True)


def get_user_position_file_path(user):
    if user.position and user.has_position_valid():
        return (
            user.position.dashboard_data_position.file_path
            if not user.dashboard_data_uri
            and not user.is_have_contact_support_status
            and hasattr(user.position, "dashboard_data_position")
            else get_media_url(user.dashboard_data_uri)
        )
    return ""


def add_sale_logs(user, event, detail, lead_id=None, timestamp=None):
    """
    Add a sale log entry for a user.

    Args:
        user: User instance
        event: String describing the event
        detail: String with additional details about the event
        lead_id: Optional string identifier for the lead
        timestamp: Optional datetime for when the event occurred
    """
    if user.role == choices.SALE:
        # Check for duplicate record
        existing_log = SaleLog.objects.filter(user=user, event=event, lead_id=lead_id, timestamp=timestamp).first()

        if not existing_log:
            SaleLog.objects.create(user=user, event=event, detail=detail, lead_id=lead_id, timestamp=timestamp)
