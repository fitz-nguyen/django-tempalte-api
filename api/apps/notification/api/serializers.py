from rest_framework import serializers

from apps.notification.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id",
            "verb",
            "title",
            "content",
            "status",
            "read",
            "created",
            "payload",
            "meta",
        )

    # def get_translate(self, obj):
    #     meta = obj.meta
    #     if meta:
    #         params = meta.get("params", [])
    #         messages = meta.get("message", [])
    #         result = []
    #         for item in messages:
    #             result.append(
    #                 {
    #                     "title": item.get("title", "").format(*params),
    #                     "message": item.get("message", "").format(*params),
    #                     "lang_code": item.get("lang_code", "").format(*params),
    #                 }
    #             )
    #         return result
    #     return []
