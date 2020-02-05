# -*- coding: utf-8 -*-

from .base import Field, ValidationException

import re


class String(Field):
    pattern = None  # regex를 기반으로한 accept 패턴
    length = None  # length descriptor 를 이용한 validation

    def get_scheme(self):
        data = super().get_scheme()

        data.update({
            "type": "string"
        })

        if self.pattern:
            data["pattern"] = self.pattern

        if self.length:
            if type(self.length) == dict:
                if "min" in self.length:
                    data["minLength"] = self.length["min"]
                if "max" in self.length:
                    data["maxLength"] = self.length["max"]
            elif type(self.length) == int:
                data["minLength"] = self.length
                data["maxLength"] = self.length

        return data

    def validation(self, data):
        data = super().validation(data)

        if data is not None:
            if self.length:
                if type(self.length) == dict:
                    if "min" in self.length:
                        if len(data) < self.length["min"]:
                            raise LengthNotMatchException()

                    if "max" in self.length:
                        if len(data) > self.length["max"]:
                            raise LengthNotMatchException()
                elif type(self.length) == int:
                    if len(data) != self.length:
                        raise LengthNotMatchException()

            if self.pattern:
                if not re.compile(self.pattern).match(data):
                    raise PatternNotMatchException()

            return data

        return None


class Enum(String):
    type = None
    nullstr = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.enum = [e.name.lower() for e in self.type]

        if self.nullstr is not None:
            self.enum.append(self.nullstr)

    def validation(self, data) -> type:
        data = super().validation(data)

        if data is None:
            return None

        if self.nullstr is not None and data == self.nullstr:
            return None

        if type(data) == self.type:
            return data

        return self.find(self.type, data)

    @classmethod
    def mapping(cls, type, value):
        return next(e.name.lower() for e in type if e.value == value)

    @classmethod
    def find(cls, type, name):
        return next(e for e in type if e.name.lower() == name.lower())


class JWT(String):
    pattern = r".*\..*\..*"
    signature = ""


class LengthNotMatchException(ValidationException):
    pass


class PatternNotMatchException(ValidationException):
    pass
