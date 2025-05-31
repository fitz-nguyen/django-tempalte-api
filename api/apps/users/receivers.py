from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.signals import email_confirmed
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from apps.core.utils import get_logger
from apps.users.models import User
from apps.users.signals import user_avatar_updated_signal, user_signup_signal
from apps.users.tasks import create_thumbnail_task, post_save_update_user_task

# logger = get_logger(__name__)
#
#
# @receiver(post_save, sender=Position)
# def do_something_when_user_updated(sender, instance: Position, created, **kwargs):
#     User.objects.filter(
#         position_id=instance.id,
#     ).update(position_value_mapping=instance.value_mapping, race_title=instance.race_type)
#
#
# @receiver(user_avatar_updated_signal)
# @receiver(user_signup_signal)
# def create_avatar_thumbnail(sender, user: User, **kwargs):
#     if user.avatar:
#         transaction.on_commit(lambda: create_thumbnail_task.delay(user.pk))
#


@receiver(post_save, sender=User)
def post_save_user_receiver(sender, instance: User, **kwargs):
    if getattr(instance, "from_admin_site", False):
        if not kwargs["created"]:
            post_save_update_user_task(instance.id)
        else:
            # only send email confirmation here when created in Django Admin site
            email_address = EmailAddress.objects.filter(user=instance, email=instance.email).first()

            if not email_address:
                email_address = EmailAddress.objects.create(
                    user=instance, email=instance.email, verified=instance.email_verified, primary=True
                )
            # send email confirmation
            EmailConfirmation.objects.delete_expired_confirmations()
            qs = EmailConfirmation.objects.all_valid().filter(email_address=email_address)
            if not qs.exists():
                email_confirmation = EmailConfirmation.create(email_address=email_address)
            else:
                email_confirmation = qs.first()

            # Send
            email_confirmation.send(signup=True)


@receiver(email_confirmed)
def update_user_email_verified(sender, request, email_address, **kwargs):
    email_address.user.email_verified = True
    email_address.user.save()
    email_address.set_as_primary()


#
# @receiver(post_save, sender=CampaignInvite)
# def push_invite_fcm(sender, created: bool, instance: CampaignInvite, **kwargs):
#     if created and instance.to_user:
#         transaction.on_commit(
#             lambda: push_invite_fcm_task.delay(invite_id=str(instance.id), send_noti=instance.to_user.notification)
#         )
#
#
# @receiver(pre_delete, sender=CampaignManager)
# @receiver(pre_delete, sender=User)
# def pre_delete_manager_receiver(sender, instance, **kwargs):
#     if instance.role == CAMPAIGN_MANAGER:
#         candidate_ids = CampaignManagerTeam.objects.filter(manager_id=instance.id).values_list(
#             "candidate_id", flat=True
#         )
#         for candidate_id in candidate_ids:
#             update_managed_by_for_candidate(candidate_id, exclude_manager_id=instance.id)
#
#
# @receiver(post_delete, sender=BlockWalker)
# @receiver(post_delete, sender=CampaignManager)
# @receiver(post_delete, sender=User)
# def user_receiver(sender, instance, **kwargs):
#     ResetPasswordOTP.objects.filter(user=instance).delete()
#     if instance.role in [BLOCK_WALKER, CAMPAIGN_MANAGER]:
#         CampaignInvite.objects.filter(to_email=instance.email).delete()
#
#
# @receiver(post_delete, sender=Candidate)
# @receiver(post_delete, sender=User)
# def delete_user_receiver(sender, instance, **kwargs):
#     if instance.role == CANDIDATE:
#         ContactSupportStatus.objects.filter(id=instance.id).delete()
