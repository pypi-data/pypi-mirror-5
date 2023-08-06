# -*- coding: utf-8 -*-

import json

from models import BulkList

from urllib import urlencode
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.concurrent import return_future


class ESConnection(object):

    def __init__(self, host='localhost', port='9200', io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        self.url = "http://%(host)s:%(port)s" % {"host": host, "port": port}
        self.bulk = BulkList()
        self.client = AsyncHTTPClient(self.io_loop)

    def create_path(self, method, **kwargs):
        index = kwargs.get('index', '_all')
        type_ = '/' + kwargs.get('type') if 'type' in kwargs else ''
        size = kwargs.get('size', 10)
        page = kwargs.get('page', 1)
        from_ = (page - 1) * size
        routing = kwargs.get('routing', '')
        jsonp_callback = kwargs.get('jsonp_callback', '')
        parameters = {'from': from_, 'size': size}
        if routing:
            parameters["routing"] = routing
        path = "/%(index)s%(type)s/_%(method)s?%(querystring)s%(jsonp_callback)s" % {
            "querystring": urlencode(parameters),
            "method": method,
            "index": index,
            "type": type_,
            "jsonp_callback": "&callback=" + jsonp_callback if jsonp_callback else ""
        }
        return path

    @return_future
    def search(self, callback, **kwargs):
        path = self.create_path("search", **kwargs)
        source = json.dumps(kwargs.get('source', {"query": {"query_string": {"query": "*"}}}))
        self.post_by_path(path, callback, source)

    def multi_search(self, index, source):
        self.bulk.add(index, source)

    @return_future
    def apply_search(self, callback):
        path = "/_msearch"
        source = self.bulk.prepare_search()
        self.post_by_path(path, callback, source=source)

    def post_by_path(self, path, callback, source):
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        request_http = HTTPRequest(url, method="POST", body=source)
        self.client.fetch(request=request_http, callback=callback)

    @return_future
    def get_by_path(self, path, callback):
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        self.client.fetch(url, callback)

    @return_future
    def get(self, index, type, uid, callback):
        def to_dict_callback(response):
            source = json.loads(response.body).get('_source', {})
            callback(source)
        self.request_document(index, type, uid, callback=to_dict_callback)

    @return_future
    def put(self, index, type, uid, contents, parameters=None, callback=None):
        self.request_document(
            index, type, uid, "PUT", body=json.dumps(contents),
            parameters=parameters, callback=callback)

    @return_future
    def delete(self, index, type, uid, parameters=None, callback=None):
        self.request_document(index, type, uid, "DELETE", parameters=parameters, callback=callback)

    @return_future
    def count(self, index="_all", type=None, source='', parameters=None, callback=None):
        path = '/{}'.format(index)

        if type:
            path += '/{}'.format(type)

        path += '/_count'

        if parameters:
            path += '?{}'.format(urlencode(parameters or {}))

        if source:
            source = json.dumps(source['query'])

        self.post_by_path(path=path, callback=callback, source=source)

    def request_document(self, index, type, uid, method="GET", body=None, parameters=None, callback=None):
        path = '/{index}/{type}/{uid}'.format(**locals())
        url = '%(url)s%(path)s?%(querystring)s' % {
            "url": self.url,
            "path": path,
            "querystring": urlencode(parameters or {})
        }
        request_arguments = dict(method=method)

        if body is not None:
            request_arguments['body'] = body

        request = HTTPRequest(url, **request_arguments)
        self.client.fetch(request, callback)
