from django.dispatch import Signal

dispatch_uploaded_file = Signal(["uploaded_file"])

dispatch_mark_file_used = Signal(["uploaded_file"])

dispatch_mark_file_deleted = Signal(["uploaded_file"])

dispatch_create_thumbnail = Signal(["uploaded_file"])
