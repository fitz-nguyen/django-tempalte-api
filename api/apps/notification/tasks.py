from apps.core.celery import app
from apps.notification import message as noti_messages
from apps.notification.pushers import FireBasePusher
from apps.notification.services.manager import NotificationManager
from apps.users.models import User


@app.task
def send_provider_arrive_notification_task(user_ids, id, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)

    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderArriveMessage(user=user_sub, order_id=order_id, id=id, id_order=id_order)
        )
        FireBasePusher().send_data_message(
            noti_messages.HasArrivedSilentMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_provider_appointment_scheduled_notification_task(user_ids, order_id, id_order, patient_name):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderAppointmentScheduledMessage(
                user=user_sub, order_id=order_id, id_order=id_order, patient_name=patient_name
            )
        )


@app.task
def send_customer_appointment_scheduled_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerAppointmentScheduledMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_customer_update_appointment_datetime_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerUpdateAppointmentDatetimeMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_customer_cancel_order_notification_task(user_ids, order_id, id_order, patient_name):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerCancelOrderMessage(
                user=user_sub, order_id=order_id, id_order=id_order, patient_name=patient_name
            )
        )


@app.task
def send_customer_send_tip_notification_task(user_ids, order_id, patient_id, id_order, amount):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    patient = User.objects.filter(id=patient_id).first()
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerSendTipMessage(
                user=user_sub, order_id=order_id, actor=patient, id_order=id_order, amount=amount
            )
        )


@app.task
def send_provider_complete_payment_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderCompletePaymentMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_provider_finish_order_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderFinishOrderMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_provider_start_shipping_order_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderStartShippingOrderMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_provider_order_complete_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderOrderCompleteMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_patient_submit_rate_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.PatientSubmitRateMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_provider_order_cancelled_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.ProviderOrderCancelledMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_refund_transaction_notification_task(user_ids, order_id, id_order, amount):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.RefundTransactionMessage(user=user_sub, order_id=order_id, id_order=id_order, amount=amount)
        )


@app.task
def send_customer_cancel_order_to_patient_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerCancelOrderToPatientMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_customer_auto_cancel_order_to_patient_notification_task(user_ids, order_id, id_order):
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerAutoCancelOrderToPatientMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )


@app.task
def send_customer_update_order_notification_task(user_ids, order_id, id_order):
    """Send to provider when customer update order"""
    users = User.objects.filter(id__in=user_ids, is_active=True)
    for user_sub in users:
        NotificationManager.send(
            noti_messages.CustomerUpdateOrderMessage(user=user_sub, order_id=order_id, id_order=id_order)
        )
