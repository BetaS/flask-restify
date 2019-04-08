# -*- coding: utf-8 -*-

from .base import Field, ValidationException


class Boolean(Field):
    def get_scheme(self):
        data = super().get_scheme()

        data.update({
            "type": "boolean",
            "format": ""
        })

        return data

    def validation(self, data):
        if data is None:
            return super().validation(None)

        if type(data) == str:
            data = data.lower() in [1, "1", "true", "yes"]

        try:
            data = bool(data)
        except (TypeError, ValueError):
            data = None

        return super().validation(data)


class Number(Field):
    range = None  # 값 입력 범위

    def get_scheme(self):
        data = super().get_scheme()

        data.update({
            "type": "number",
            "format": ""
        })

        if self.range:
            if "min" in self.range:
                data["minimum"] = self.range["min"]

            if "max" in self.range:
                data["maximum"] = self.range["max"]

        return data

    def validation(self, data):
        data = super().validation(data)

        if data is not None:
            if self.range:
                if type(self.range) != dict:
                    raise TypeError()

                if "min" in self.range:
                    if data < self.range["min"]:
                        raise RangeException()

                if "max" in self.range:
                    if data > self.range["max"]:
                        raise RangeException()

        return data


class Integer(Number):
    def get_scheme(self):
        data = super().get_scheme()

        data.update({
            "type": "integer",
            "format": "int32"
        })

        return data

    def validation(self, data):
        try:
            data = int(data)
        except (TypeError, ValueError):
            data = None

        return super().validation(data)


class Float(Number):
    def get_scheme(self):
        data = super().get_scheme()

        data.update({
            "type": "number",
            "format": "float"
        })

        return data

    def validation(self, data):
        try:
            data = float(data)
        except (TypeError, ValueError):
            data = None

        return super().validation(data)


class RangeException(ValidationException):
    def __init__(self):
        super().__init__("value must satisfy range property")
