class OwnerMixin:
    def get_current_user(self):
        request = self.context.get("request")
        return request.user if request else None
