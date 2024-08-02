# coding: utf-8

from django.http import HttpResponse
from django_decorators.request import *


@GET  # Http method is get
def function1(params: RequestParam):
    """all params, params is dict
    """
    return HttpResponse(params)


@GET
def function2(
        id: RequestParam('id'),
        name: RequestParam('name', null=True),  # name can null
        user: RequestUser,
        headers: RequestHeaders,
        cookies: RequestCookies,
        ip: RequestIP
):
    return HttpResponse({
        'id': id,
        'name': name,
        'user': user,
        'headers': headers,
        'cookies': cookies,
        'ip': ip
    })


@POST  # Http method is post
def function3(body: RequestBody):
    """body is str
    """
    return HttpResponse(body)


@DELETE  # Http method is delete
def function4(body: RequestJsonBody):
    """body transform to json
    """
    return HttpResponse(body)


@PUT  # Http method is put
def function5(
        id: RequestJsonBody('id'),
        name: RequestJsonBody('name', null=True),
        sex: RequestJsonBody('detail.sex')
):
    """
    request body:
    {
        "id": 1,
        "name": "Joe",
        "detail": {"sex": "M"}
    }
    """
    return HttpResponse({
        'id': id,
        'name': name,
        'sex': sex
    })


@POST
def function6(file: RequestFile, file2: RequestFile('file2', null=True)):
    """upload file
    """
    return HttpResponse('file is not None and file2 is None')


# @Rest('OPTION')  # Http method is custom: option
@Rest(['OPTION', 'GET'])  # Http method is custom: option or get
def function7(request):
    """request is django http request
    """
    return HttpResponse(request is not None)
