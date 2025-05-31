from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from apps.systems.utils import SystemConfigCache
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from apps.users_auth.services import resend_confirmation_email


class AccountAdapter(DefaultAccountAdapter):
    def respond_email_verification_sent(self, request, user):
        """
        We don't need this redirect.
        """
        pass

    def get_email_confirmation_url(self, request, emailconfirmation, **kwargs):
        slug = kwargs.get("slug") if "slug" in kwargs else "account-created"
        return "{}/{}/{}".format(settings.FRONTEND_BASE_URL.rstrip("/"), slug, emailconfirmation.key)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "name": emailconfirmation.email_address.user.name,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
            "expire_day": settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS,
            "frontend_url": settings.FRONTEND_BASE_URL,
            "footer_image_url": SystemConfigCache().email_footer_url,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_approve_under_review"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

    def pre_login(self, request, user, *, email_verification, signal_kwargs, email, signup, redirect_url):
        # if not user.is_active:
        #     return self.respond_user_inactive(request, user)
        EmailAddress.objects.create(user=user, email=user.email, primary=True)
        return user
