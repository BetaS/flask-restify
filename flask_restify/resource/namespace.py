# -*- coding: utf-8 -*-


class Namespace:
    api = None
    context = None
    tag = ""
    path = ""
    description = ""

    routes = {}

    def __init__(self, api, tag, path, description, context):
        self.api = api
        self.tag = tag
        self.path = path
        self.description = description
        self.context = context
        self.routes = {}
