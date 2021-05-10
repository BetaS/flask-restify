# -*- coding: utf-8 -*-

from flask_restify.resource.namespace import Namespace

from flask_restify import fields

import re


class SwaggerDoc:
    title = ""
    description = ""

    namespace: {str: dict} = {}
    path: {str: dict} = {}

    def __init__(self, title, description, version):
        self.title = title
        self.description = description
        self.version = version

    def add_namespace(self, path: str, ns: Namespace):
        # 1. 이미 있나 확인 후
        if ns.tag in self.namespace:
            raise Exception("Namespace '{0}' already exists.".format(ns.tag))

        self.namespace[ns.tag] = {
            "name": ns.tag,
            "description": ns.description
        }

        for route, methods in ns.routes.items():
            route = re.sub(r"<(.*?)>", r"{\g<1>}", route)

            full_path = path+route

            if full_path in self.path:
                raise Exception("Path '{0}' already exists.".format(full_path))

            self.path[full_path] = {}
            for method, data in methods.items():
                params = []
                bodies = {}
                forms = {}
                responses = {}

                for name, param in data["func"].params.items():
                    if param["in"] in ["path", "query", "header"]:
                        d = {
                            "name": name,
                            "in": param["in"]
                        }
                        d.update(param["data"].get_swagger())
                        params.append(d)
                    elif param["in"] == "body":
                        bodies[name] = param["data"]
                    elif param["in"] == "form":
                        forms[name] = param["data"]

                for code, res in data["func"].responses.items():
                    d = {
                        "description": res["description"]
                    }

                    if type(res["model"]) == dict:
                        res["model"] = fields.Object(data=res["model"])
                    elif type(res["model"]) == list:
                        res["model"] = fields.Array(item=res["model"][0])

                    if isinstance(res["model"], (fields.Object, fields.Array)):
                        d["content"] = {
                            "application/json": res["model"].get_swagger(for_response=True)
                        }

                    responses[code] = d

                oper = {
                    "operationId": data["func"].__module__+"."+data["func"].__qualname__,
                    "summary": data["title"],
                    "tags": data["tags"]
                }

                if len(params):
                    oper["parameters"] = params

                if len(bodies) > 0 or len(forms) > 0:
                    content = {}

                    if len(bodies) > 0:
                        content["application/json"] = fields.Object(data=bodies).get_swagger(for_response=True)

                    if len(forms) > 0:
                        content["application/x-www-form-urlencoded"] = fields.Object(data=forms).get_swagger(for_response=True)

                    oper["requestBody"] = {
                        "required": True,
                        "content": content
                    }

                if len(responses) > 0:
                    oper["responses"] = responses

                if "description" in data:
                    oper["description"] = data["description"]

                if data["func"].auth:
                    oper["security"] = [{"auth": []}]

                self.path[full_path][method] = oper

    def _info(self):
        return {
            "title": self.title,
            "description": self.description,
            "version": self.version
        }

    def _path(self):
        return self.path

    def to_json(self):
        tags = []

        for tag, ns in self.namespace.items():
            tags.append(ns)

        return {
            "openapi": "3.0.0",
            "info": self._info(),
            "paths": self._path(),
            "components": {
                "securitySchemes": {
                    "auth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "tags": tags
        }


def parameterize(model: dict):
    result = []

    for k, v in model.items():
        item = {"name": k}
        if type(v) == dict:
            v = fields.Object(data=v)
        item.update(v.get_swagger())
        result.append(item)

    return result


if __name__ == "__main__":
    # 1. 하나의 dict가 있는 경우
    print(parameterize({
        "id": fields.Integer(),
        "name": fields.String()
    }))

    # 2. dict가 중첩된 경우
    print(parameterize({
        "id": fields.Integer(),
        "name": fields.String(),
        "userinfo": {
            "email": fields.String(pattern=r"^.*?\|+$", example="test"),
            "passwd": fields.String()
        }
    }))
