# -*- coding: utf-8 -*-


class Field:
    description = ""
    default = None
    optional = False
    example = None
    place = None

    enum = []

    def __init__(self, **kwargs):
        for k in self.__get_class_variables():
            if k in kwargs:
                vars(self)[k] = kwargs[k]

    def __get_class_variables(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

    def get_swagger(self, for_response=False):
        data = {}

        if len(self.description) > 0:
            data["description"] = self.description

        if not for_response:
            if self.place:
                data["in"] = self.place

            if not self.optional:
                data["required"] = True

        scheme = self.get_scheme()
        if len(scheme) > 0:
            data["schema"] = scheme

        return data

    def get_scheme(self):
        data = {}

        if self.enum and len(self.enum) > 0:
            data["enum"] = self.enum

        if self.default:
            data["default"] = str(self.default)

        if self.example:
            if type(self.example) in [str, int, float, bool]:
                data["example"] = self.example
            else:
                data["example"] = str(self.example)

        return data

    def validation(self, data):
        if data is None and self.default is not None:
            return self.default

        if not self.optional:
            if data is None:
                raise RequiredFieldException()

        if len(self.enum) > 0:
            if data is not None and not (data in self.enum):
                raise ValidationException("only accept one of '{0}'s".format(self.enum))

        return data


class Object(Field):
    data: {str: Field} = {}

    def get_scheme(self):
        props = {}
        requires = []

        for k, v in self.data.items():
            props[k] = v.get_swagger()
            if "required" in props[k]:
                if props[k]["required"]:
                    requires.append(k)

                del props[k]["required"]

            if "schema" in props[k]:
                props[k].update(props[k]["schema"])

                del props[k]["schema"]

        data = {
            "type": "object",
            "properties": props
        }

        if len(requires) > 0:
            data["required"] = requires

        return data


class Array(Field):
    item: Field = None

    def get_scheme(self):
        data = {
            "type": "array",
            "items": self.item.get_scheme()
        }

        return data


class ValidationException(BaseException):
    pass


class RequiredFieldException(ValidationException):
    pass
