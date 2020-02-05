# -*- coding: utf-8 -*-

from flask import request
from flask_restify.util.error import HttpError
from flask_restify.util.parser import parse_params
from functools import wraps
import inspect


def route(ns, method="get", path="", description="", tags=[]):
    method = method.lower()

    def decorator(f):
        title = f.__module__+"."+f.__qualname__

        # 1. 해당 path가 이미 존재하는지 체크
        target = {}
        if path in ns.routes:
            target = ns.routes[path]

        # 2. 해당 method가 이미 존재하는지 체크
        if method in target:
            print(ns.routes)
            raise ValueError("specific path '{0}'s method ('{1}') is already exist.".format(path, method))

        # route 객체 구성
        data = {"title": title, "func": f, "tags": [ns.tag]+tags}

        if not hasattr(f, "params"):
            f.params = {}

        if not hasattr(f, "responses"):
            f.responses = {}

        if not hasattr(f, "auth"):
            f.auth = False

        if description and len(description) > 0:
            data["description"] = description

        # 해당 method에 내용 등록
        target[method] = data

        # 해당 route 덮어씀
        ns.routes[path] = target

        return f

    return decorator


def parameter(path=None, header=None, body=None, query=None, form=None):
    def decorator(f):
        # 파라미터가 존재하지 않는다면
        if not hasattr(f, "params"):
            f.params = {}

        # 등록시 모든 field가 unique한지 체크하여 documentation에 등록
        for place, x in [("path", path), ("header", header), ("body", body), ("query", query), ("form", form)]:
            if x:
                for name, d in x.items():
                    if name in f.params:
                        raise Exception("param '{0}' is already exists".format(name))

                    f.params[name] = {"in": place, "data": d}

        @wraps(f)
        def wrapped_f(*args, **kwargs):
            req = []
            if path:
                req.append((path, kwargs))

            if header:
                req.append((header, request.headers))

            if body:
                req.append((body, request.get_json()))

            if query:
                req.append((query, request.args))

            if form:
                req.append((form, request.form))

            # 파싱할 내용이 있을때만
            blueprints = {}
            params = {x: None for x in inspect.signature(f).parameters}
            for target, source in req:
                blueprints.update(target)
                params.update(source)

            result = parse_params(blueprints, params, kwargs)

            return f(*args, **result)

        return wrapped_f

    return decorator


def response(code=200, description="", model=None):
    if model is None:
        model = {}

    def decorator(f):
        # 응답 코드가 존재하지 않는다면
        if not hasattr(f, "responses"):
            f.responses = {}

        if code in f.responses:
            raise Exception("code '{0}' already exists.".format(code))

        f.responses[code] = {"description": description, "model": model}

        @wraps(f)
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped_f

    return decorator


def error(code, description="", exception: type(BaseException) = BaseException):
    def decorator(f):
        # 응답 코드가 존재하지 않는다면
        if not hasattr(f, "responses"):
            f.responses = {}

        if code in f.responses:
            f.responses[code]["description"] += "<br/>" + description
        else:
            f.responses[code] = {"description": description, "model": None}

        @wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exception as e:
                raise HttpError(code, description, str(e))

        return wrapped_f

    return decorator


def authenticate(optional=False):
    def decorator(f):
        f.auth = True

        # 응답 코드가 존재하지 않는다면
        if not hasattr(f, "responses"):
            f.responses = {}

        if 401 in f.responses:
            raise Exception("code '{0}' already exists.".format(401))

        f.responses[401] = {"description": "인증되지 않음", "model": None}

        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if args[0].session is None and not optional:
                raise HttpError(401, "인증이 필요합니다.")

            return f(*args, **kwargs)

        return wrapped_f

    return decorator
