# -*- coding: utf-8 -*-


class HttpError(BaseException):
    code: int
    message: str
    description: str

    def __init__(self, code: int, message: str, description: str = None):
        self.code = code
        self.message = message
        self.description = description

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "description": self.description
        }
