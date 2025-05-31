from apps.notification import choices
from apps.notification.services.message import NotificationMessage

PROVIDER_ARRIVE_TITLE = "Your order #{} has arrived!"
PROVIDER_ARRIVE_MESSAGE = "Your order #{} has arrived!"

PROVIDER_APPOINTMENT_SCHEDULED_TITLE = "You have received a new order from {}"
PROVIDER_APPOINTMENT_SCHEDULED_MESSAGE = "You have received a new order from {}."

CUSTOMER_APPOINTMENT_SCHEDULED_TITLE = "We found you a provider!"
CUSTOMER_APPOINTMENT_SCHEDULED_MESSAGE = "We found you a provider!"

CUSTOMER_UPDATE_APPOINTMENT_DATETIME_TITLE = "The datetime has been updated"
CUSTOMER_UPDATE_APPOINTMENT_DATETIME_MESSAGE = "The datetime has been updated."

PROVIDER_ORDER_CANCELLED_TITLE = "Unfortunately, Patient {} canceled the order #{}"
PROVIDER_ORDER_CANCELLED_MESSAGE = "Unfortunately, Patient {} canceled the order #{}."

PROVIDER_RECEIVE_TIP_TITLE = "Congrat! You have just received a tip of ${} from your order #{}"
PROVIDER_RECEIVE_TIP_MESSAGE = "Congrat! You have just received a tip of ${} from your order #{}."

PROVIDER_COMPLETE_FINAL_PAYMENT_TITLE = "Thank you. Payment for order #{} has been processed successfully"
PROVIDER_COMPLETE_FINAL_PAYMENT_MESSAGE = "Thank you. Payment for order #{} has been processed successfully"


PROVIDER_START_SHIPPING_ORDER_TITLE = "Your order #{} is on its way"
PROVIDER_START_SHIPPING_ORDER_MESSAGE = "Your order #{} is on its way."

PROVIDER_FINISH_ORDER_TITLE = "The provider confirms the order #{} is complete. Please complete your payment"
PROVIDER_FINISH_ORDER_MESSAGE = "The provider confirms the order #{} is complete. Please complete your payment."

PROVIDER_ORDER_COMPLETE_TITLE = "Thank you. The order #{} has been completed successfully"
PROVIDER_ORDER_COMPLETE_MESSAGE = "Thank you. The order #{} has been completed successfully."

PATIENT_SUBMIT_RATE_TITLE = "You just got a new review"
PATIENT_SUBMIT_RATE_MESSAGE = "You just got a new review."

PROVIDER_CANCELLED_ORDER_TITLE = "Unfortunately, the provider is not available right now Finding you a nearby provider"
PROVIDER_CANCELLED_ORDER_MESSAGE = (
    "Unfortunately, the provider is not available right now. Finding you a nearby provider."
)


REFUND_TRANSACTION_TITLE = "You have a refund ${} from order #{}"
REFUND_TRANSACTION_MESSAGE = "You have a refund ${} from order #{}."

CUSTOMER_CANCEL_ORDER_TO_PATIENT_TITLE = "Order Cancelled"
CUSTOMER_CANCEL_ORDER_TO_PATIENT_MESSAGE = (
    "You have successfully cancelled your order #{}. Your refund's on the way (if you were charged)."
)

CUSTOMER_AUTO_CANCEL_ORDER_TO_PATIENT_TITLE = "Order Cancelled"
CUSTOMER_AUTO_CANCEL_ORDER_TO_PATIENT_MESSAGE = (
    "Your order #{} has been expired. Your refund's on the way (if you were charged)."
)

CUSTOMER_UPDATE_ORDER_TITLE = "The order #[FORMAT_TEXT] has been updated"
CUSTOMER_UPDATE_ORDER_MESSAGE = "The order #[FORMAT_TEXT] has been updated."

PROVIDER_REMIND_SHIPPING_TITLE = "Order #{} must be started by {}. Get ready to finish it!"
PROVIDER_REMIND_SHIPPING_MESSAGE = "Order #{} must be started by {}. Get ready to finish it!"


class BaseMessage(NotificationMessage):

    language_key = ""

    def __init__(self, user):
        self._user = user

    @property
    def user(self):
        return self._user

    @property
    def target_object(self):
        return None

    @property
    def payload(self):
        return self._data

    @property
    def data(self):
        return self._data

    @property
    def meta_params(self):
        return []


class HasArrivedSilentMessage(BaseMessage):
    def __init__(self, user, order_id, id_order):
        self._user = user
        self._data = {"t": self.verb, "d": "0", "order_id": str(order_id), "id_order": str(id_order)}

    @property
    def title(self) -> str:
        return ""

    @property
    def content(self):
        return ""

    @property
    def verb(self):
        return choices.HAS_ARRIVED_SILENT_PUSH


class ProviderRemindShippingSilentMessage(BaseMessage):
    def __init__(self, user, order_id, id_order, start_time, status):
        self._user = user
        self._data = {
            "t": self.verb,
            "d": "0",
            "order_id": str(order_id),
            "id_order": str(id_order),
            "status": str(status),
            "start_time": str(start_time),
        }

    @property
    def title(self) -> str:
        return ""

    @property
    def content(self):
        return ""

    @property
    def verb(self):
        return choices.PROVIDER_REMIND_SHIPPING_SILENT_PUSH
