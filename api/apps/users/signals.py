from django.dispatch import Signal

user_signup_signal = Signal(["user"])
user_avatar_updated_signal = Signal(["user"])
