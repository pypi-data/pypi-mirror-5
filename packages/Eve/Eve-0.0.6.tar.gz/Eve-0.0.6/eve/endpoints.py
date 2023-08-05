# -*- coding: utf-8 -*-

"""
    eve.endpoints
    ~~~~~~~~~~~~~

    This module implements the API endpoints. Each endpoint (resource, item,
    home) invokes the appropriate method handler, returning its response
    to the client, properly rendered.

    :copyright: (c) 2012 by Nicola Iarocci.
    :license: BSD, see LICENSE for more details.
"""

from methods import get, getitem, post, patch, delete, delete_resource
from flask import request, abort
from render import send_response
from eve.auth import requires_auth
from eve.utils import resource_uri, config


def collections_endpoint(url):
    """ Resource endpoint handler

    :param url: the url that led here

    .. versionchanged:: 0.0.6
       Support for HEAD requests

    .. versionchanged:: 0.0.2
        Support for DELETE resource method.
    """

    resource = config.RESOURCES[url]
    response = None
    if request.method in ('GET', 'HEAD'):
        response = get(resource)
    elif request.method == 'POST':
        response = post(resource)
    elif request.method == 'DELETE':
        response = delete_resource(resource)
    return send_response(resource, response)


def item_endpoint(url, **lookup):
    """ Item endpoint handler

    :param url: the url that led here
    :param lookup: the query

    .. versionchanged:: 0.0.6
       Support for HEAD requests
    """
    resource = config.RESOURCES[url]
    response = None
    if request.method in ('GET', 'HEAD'):
        response = getitem(resource, **lookup)
    elif request.method == 'PATCH' or (request.method == 'POST' and
                                       request.headers.get(
                                           'X-HTTP-Method-Override')):
        response = patch(resource, **lookup)
    elif request.method == 'DELETE':
        response = delete(resource, **lookup)
    elif request.method == 'POST':
        # We are supporting PATCH via POST with X-HTTP-Method-Override (see
        # above), therefore we must explicitly handle this case.
        abort(405)
    return send_response(resource, response)


@requires_auth('home')
def home_endpoint():
    """ Home/API entry point. Will provide links to each available resource
    """
    response = {}
    links = []
    for resource in config.DOMAIN.keys():
        links.append({'href': '%s' % resource_uri(resource),
                      'title': '%s' % config.URLS[resource]})
    response['_links'] = {'child': links}
    return send_response(None, (response,))
