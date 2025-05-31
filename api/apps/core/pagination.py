from base64 import b64encode
from collections import OrderedDict
from urllib import parse

from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class CursorSetPagination(CursorPagination):
    page_size_query_param = "limit"
    ordering = "id"


class CustomCursorPagination(CursorSetPagination):
    def encode_cursor(self, cursor):
        """
        Given a Cursor instance, return an url with encoded cursor.
        """
        tokens = {}
        if cursor.offset != 0:
            tokens["o"] = str(cursor.offset)
        if cursor.reverse:
            tokens["r"] = "1"
        if cursor.position is not None:
            tokens["p"] = cursor.position

        querystring = parse.urlencode(tokens, doseq=True)
        encoded = b64encode(querystring.encode("ascii")).decode("ascii")
        return replace_query_param(self.base_url, self.cursor_query_param, encoded), encoded

    def get_paginated_response(self, data):
        next_url, next_cursor = self.get_next_link() if self.get_next_link() else (None, None)
        previous_url, previous_cursor = self.get_previous_link() if self.get_previous_link() else (None, None)
        return Response(
            OrderedDict(
                [
                    ("next", next_url),
                    ("next_cursor", next_cursor),
                    ("previous", previous_url),
                    ("previous_cursor", previous_cursor),
                    ("results", data),
                ]
            )
        )


class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = "limit"
