# -*- coding: utf-8 -*-

from flask_restify.docs import swagger, ui
from flask_restify.util import error

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy

import json
import traceback
import sys
import atexit


class RequestContext:
    pass


class BaseAPI:
    app: Flask = None
    db: SQLAlchemy = SQLAlchemy()
    namespaces = {}
    docs: swagger.SwaggerDoc = None

    def __init__(self, name="", description="", version="1.0.0"):
        self.endpoint_map = {}

        self.app = Flask(name)
        self.docs = swagger.SwaggerDoc(name, description, version)

        self.swaggerui = ui.get_swaggerui_blueprint(
            "/docs",
            "/swagger.json",
            config={
                'app_name': name,
                "displayRequestDuration": True,
                "jsonEditor": True
            }
        )

    def init_server(self, config="app.config.DevelopmentConfig"):
        self.app.config.from_object(config)

        self.db.init_app(self.app)
        atexit.register(self.on_exit)

        self.on_init()

        self.app.register_blueprint(self.swaggerui, url_prefix="/docs")

        self.app.add_url_rule("/swagger.json", "swagger",
                              lambda *args, **kwargs: Response(response=json.dumps(self.docs.to_json()), status=200,
                                                               mimetype="application/json"))

        for k, ns in self.namespaces.items():
            root_path = ns.path
            for p, res in ns.routes.items():
                path = root_path + p
                for method, func in res.items():
                    self.endpoint_map[func["title"]] = {"ns": ns, "func": func}
                    self.app.add_url_rule(path, func["title"], self.handle_request, methods=[method.upper(), ])

        self.app.after_request(self.after_request)

        return self.app

    def handle_request(self, *args, **kwargs):
        if request.endpoint not in self.endpoint_map:
            return Response(response="Can't find endpoint '{0}'".format(request.endpoint), status=500, mimetype="text/plain")

        ns = self.endpoint_map[request.endpoint]["ns"]
        func = self.endpoint_map[request.endpoint]["func"]

        context = ns.context()  # ns.cls()
        self.on_receive(context)

        try:
            auth_header = request.headers.get('Authorization')
            try:
                if auth_header and len(auth_header) > 0:
                    context.update_authkey(auth_header.split(" ")[1])
                else:
                    context.update_authkey("")
            except BaseException as e:
                raise error.HttpError(401, str(e))

            result = func["func"](context, *args, **kwargs)
            code = 200

            if type(result) == tuple:
                code = result[1]
                result = result[0]

            return Response(response=json.dumps(result, ensure_ascii=False), headers=context.headers, status=code, mimetype="application/json")
        except error.HttpError as e:
            self.on_error(context, e)
            return Response(response=json.dumps(e.to_dict(), ensure_ascii=False), status=e.code, mimetype="application/json")
        except Exception as e:
            self.on_error(context, error.HttpError(500, e, "Internal Server Error"))
            print(e, file=sys.stderr)
            traceback.print_tb(e.__traceback__)
            return Response(response=json.dumps({"caused_by": str(e)}), status=500, mimetype="application/json")

    # noinspection PyMethodMayBeStatic
    def after_request(self, response):
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        header['Access-Control-Allow-Methods'] = 'OPTIONS, GET, PUT, POST, HEAD, PATCH, DELETE, INDEX'
        header['Access-Control-Allow-Headers'] = 'Authorization, X-Request-ID, X-PINGOTHER, Content-Type, Accept-Language, Origin, Referer'
        header['Access-Control-Expose-Headers'] = 'X-Request-ID, X-Authorization-Update'

        # Request ID가 있을 경우 처리
        id = request.headers.get("X-Request-ID")
        if id:
            header["X-Request-ID"] = id

        return response

    def add_namespace(self, ns):
        tag = ns.tag
        path = ns.path

        if tag in self.namespaces:
            raise Exception("Namespace already exist.")

        self.namespaces[tag] = ns

        self.docs.add_namespace(path, ns)

    def on_init(self):
        pass

    def on_receive(self, context):
        pass

    def on_error(self, context, e: error.HttpError):
        pass

    def on_exit(self):
        pass