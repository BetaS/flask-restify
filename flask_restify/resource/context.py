# -*- coding: utf-8 -*-


class BaseContext:
    headers = {}

    def __init__(self, **kwargs):
        self.headers = {}

    def on_auth(self):
        pass

    def update_authkey(self, authkey):
        pass

    def set_authkey(self, authkey):
        self.headers["X-Authorization-Update"] = "Bearer {0}".format(authkey)
