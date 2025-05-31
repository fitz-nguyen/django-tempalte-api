import branchio
from django.conf import settings


def generate_branch_io_link(data):
    client = branchio.Client(settings.BRANCH_IO_CLIENT_KEY)
    response = client.create_deep_link_url(data=data, channel="web-api")
    return response[branchio.RETURN_URL]
