# -*- coding: utf-8 -*-

from ..util import error

from flask import request

from functools import wraps
import inspect


def _param_validation(name, t, v):
    try:
        return t.validation(v)  # 파싱해서 집어넣음
    except BaseException as e:
        t_name = t.__module__ + "." + t.__class__.__qualname__
        raise error.HttpError(400, "'{0}' 파라미터 형식 오류 '{1}', '{2}'->'{3}'".format(name, e, v, t_name))


# noinspection PyMethodMayBeStatic
class Namespace:
    api = None
    tag = ""
    path = ""
    description = ""

    routes = {}

    def __init__(self, api, tag, path, description):
        self.api = api
        self.tag = tag
        self.path = path
        self.description = description
        self.routes = {}

    def route(self, method="get", path="", title="", description=""):
        def decorator(f):
            # 1. 해당 path가 이미 존재하는지 체크
            target = {}
            if path in self.routes:
                target = self.routes[path]

            # 2. 해당 method가 이미 존재하는지 체크
            if method in target:
                print(self.routes)
                raise ValueError("specific path '{0}'s method ('{1}') is already exist.".format(path, method))

            # route 객체 구성
            data = {"title": title, "func": f}

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
            self.routes[path] = target

            return f

        return decorator

    def parameter(self, path=None, header=None, body=None, query=None, form=None):
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
                if len(req) > 0:
                    for target, source in req:
                        for k, v in target.items():
                            # 시스템 Parameter에 이미 내용이 존재함
                            if k in kwargs:
                                # 파싱해서 집어넣음
                                kwargs[k] = _param_validation(k, v, kwargs[k])

                            # Http Parameter에 내용이 존재함
                            elif source is not None and k in source:
                                # 파싱해서 집어넣음
                                kwargs[k] = _param_validation(k, v, source[k])

                            # 필수이지만 없음
                            elif not v.optional:
                                # 파라미터 부족 오류
                                raise error.HttpError(400, "파라미터 누락 '{0}'".format(k))

                            # positional arg 인경우 None으로 추가
                            elif k in inspect.signature(f).parameters:
                                kwargs[k] = _param_validation(k, v, None)

                return f(*args, **kwargs)

            return wrapped_f

        return decorator

    def response(self, code=200, description="", model=None):
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

    def error(self, code, description="", exception: type(BaseException) = BaseException):
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
                    raise error.HttpError(code, description, str(e))

            return wrapped_f

        return decorator

    def authenticate(self, optional=False):
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
                    raise error.HttpError(401, "인증이 필요합니다.")

                return f(*args, **kwargs)

            return wrapped_f

        return decorator
