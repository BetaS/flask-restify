# -*- coding: utf-8 -*-

from flask_restify.util.error import HttpError


def _param_validation(name, t, v: any) -> any:
    try:
        return t.validation(v)  # 파싱해서 집어넣음
    except BaseException as e:
        t_name = t.__module__ + "." + t.__class__.__qualname__
        raise HttpError(400, "'{0}' 파라미터 형식 오류 '{1}', '{2}'->'{3}'".format(name, e, v, t_name))


def parse_params(blueprint: dict, params: dict, defaults: dict={}) -> dict:
    if blueprint is None or len(blueprint) == 0:
        return defaults

    if params is None:
        params = {}

    result = {**defaults} if defaults is not None else {}

    for k, v in blueprint.items():
        # 시스템 Parameter에 이미 내용이 존재함
        if k in defaults:
            # 파싱해서 집어넣음
            result[k] = _param_validation(k, v, defaults[k])

        # Http Parameter에 내용이 존재함
        elif k in params:
            # 파싱해서 집어넣음
            result[k] = _param_validation(k, v, params[k])

        # System Parameter에 내용이 존재함
        elif k in defaults:
            # 파싱해서 집어넣음
            result[k] = _param_validation(k, v, defaults[k])

        # 옵셔널이면서 없음
        elif v.optional:
            # 파라미터 부족 오류
            result[k] = _param_validation(k, v, None)

        else:
            raise HttpError(400, "파라미터 누락 '{0}'".format(k))

    return result
