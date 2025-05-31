# from apps.uploads.models import UploadFile
# from django.contrib import admin
#
#
# @admin.register(UploadFile)
# class UploadFileAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "status",
#         "file_path",
#         "size",
#         "mime_type",
#         "storage",
#         "ip_address",
#         "user",
#         "created",
#     )
#     search_fields = (
#         "status",
#         "file_path",
#     )
#     ordering = ("-created",)
#     raw_id_fields = ("user",)
