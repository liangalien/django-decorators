# coding: utf-8


import inspect
import json

from django.views.decorators.http import require_http_methods
from django.core.handlers.wsgi import HttpRequest


class AnnotationNullException(BaseException):
    def __init__(self, field_name):
        super(AnnotationNullException, self).__init__(f'param "{field_name}" can not null')


class AnnotationRequestNotFoundException(BaseException):
    def __init__(self):
        super(AnnotationRequestNotFoundException, self).__init__(f'param request not found')


class Annotation:
    def __init__(self, null=True):
        self.null = null

    def call(self, request, name):
        result = self.handle(request)
        if not self.null and result is None:
            raise AnnotationNullException(name)
        return result

    def handle(self, request):
        return request


class RequestCookies(Annotation):
    def handle(self, request) -> dict:
        return request.COOKIES


class RequestHeaders(Annotation):
    def handle(self, request) -> dict:
        return {key[5:].lower(): value for key, value in request.META.items() if key.startswith('HTTP_')}


class RequestIP(Annotation):
    def handle(self, request) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return request.META.get('REMOTE_ADDR')


class RequestUser(Annotation):
    def __init__(self, null=False):
        super(RequestUser, self).__init__(null)

    def handle(self, request) -> str:
        return request.user


class RequestParam(Annotation):
    def __init__(self, field=None, null=False, method='GET'):
        super(RequestParam, self).__init__(null)
        self.field = field
        self.method = method

    def handle(self, request) -> [str, dict]:
        params = getattr(request, self.method).dict()
        return params.get(self.field) if self.field else params


class RequestBody(Annotation):
    def __init__(self, coding='utf-8', null=False):
        super(RequestBody, self).__init__(null)
        self.coding = coding

    def handle(self, request) -> str:
        body = request.body
        return body.decode(self.coding) if body and self.coding else body


class RequestJsonBody(RequestBody):
    def __init__(self, field=None, coding='utf-8', null=False):
        super(RequestJsonBody, self).__init__(coding, null)
        self.field = field

    def handle(self, request):
        body = super(RequestJsonBody, self).handle(request)
        if not body:
            return None

        result = json.loads(body)
        if self.field:
            fields = self.field.split('.')
            for field in fields:
                result = result.get(field, {})

            if result == {}:
                result = None

        return result


class RequestFile(Annotation):
    def __init__(self, name='file', null=False):
        super(RequestFile, self).__init__(null)
        self.name = name

    def handle(self, request):
        return request.FILES.get(self.name, None)


def rest_inspect(fn, self, request, other):
    other_idx = 0
    new_args = []
    for name, param in inspect.signature(fn).parameters.items():
        # set params from function params
        if param.annotation == inspect._empty:  # annotation is empty
            if name == 'self':  # first param is self
                new_args.append(self)
            elif name == 'request':  # first param is request
                new_args.append(request)
            elif other_idx < len(other):  # other
                new_args.append(other[other_idx])
                other_idx += 1

        # set params by annotation class
        elif isinstance(param.annotation, type):
            new_args.append(param.annotation().call(request, name))

        # set params by annotation class instance
        else:
            new_args.append(param.annotation.call(request, name))

    return new_args


class AuthType:
    Null = 0
    DEFAULT = 1
    ERP = 2
    Role = 3


def Rest(method):
    def decorate(fn):
        methods = method
        if not isinstance(methods, list):
            methods = [methods]

        @require_http_methods(methods)
        def wrapper(self_or_request, *args, **kwargs):
            if isinstance(self_or_request, HttpRequest):
                self = None
                request = self_or_request
            else:
                self = self_or_request
                args = list(args)
                request = args.pop(0)

            # create args and kwargs
            new_args = rest_inspect(fn, self, request, args)
            return fn(*new_args, **kwargs)

        return wrapper

    return decorate


GET = Rest('GET')
POST = Rest('POST')
DELETE = Rest('DELETE')
PUT = Rest('PUT')
