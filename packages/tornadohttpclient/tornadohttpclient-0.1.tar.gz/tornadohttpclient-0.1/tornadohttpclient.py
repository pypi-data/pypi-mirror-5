#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright 2013 cold
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#   Author  :   cold
#   E-mail  :   wh_linux@126.com
#   Date    :   13/04/18 16:17:25
#   Desc    :
#
"""
"""
from __future__ import absolute_import

import ssl
import time
import socket
import urllib
import urllib2
import httplib
import urlparse
import tempfile
import logging
import traceback
import cookielib
import threading
import mimetools
import mimetypes
import itertools

from functools import partial
from tornado.ioloop import IOLoop


class Form(object):
    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        self.content_type = 'multipart/form-data; boundary=%s' % self.boundary
        return

    def get_content_type(self):
        return self.content_type

    def add_field(self, name, value):
        self.form_fields.append((str(name), str(value)))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        body = fileHandle.read()
        if mimetype is None:
            mimetype = ( mimetypes.guess_type(filename)[0]
                         or
                         'applicatioin/octet-stream')
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        parts = []
        part_boundary = '--' + self.boundary

        parts.extend(
            [ part_boundary,
             'Content-Disposition: form-data; name="%s"' % name,
             '',
             value,
             ]
            for name, value in self.form_fields)
        if self.files:
            parts.extend([
                part_boundary,
                'Content-Disposition: form-data; name="%s"; filename="%s"' %\
                (field_name, filename),
                'Content-Type: %s' % content_type,
                '',
                body,
            ] for field_name, filename, content_type, body in self.files)

        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class HTTPSock(object):
    """ 构建支持Cookie的HTTP socket
    供可复用的I/O模型调用"""
    def __init__(self):
        cookiefile = tempfile.mktemp()
        self.cookiejar = cookielib.MozillaCookieJar(cookiefile)
        self.host_map = {}

    def make_get_url(self, url, params):
        return "{0}?{1}".format(url, urllib.urlencode(params))

    def make_request(self, url, form = None):
        """ 根据url 参数 构建 urllib2.Request """
        request = urllib2.Request(url)
        if isinstance(form, Form):
            request.add_header("Content-Type", form.get_content_type())
            request.add_header("Content-Length", len(str(form)))
            request.add_data(str(form))
        elif isinstance(form, (dict, list, tuple)):
            params = urllib.urlencode(form)
            request = urllib2.Request(url, params)
            request.add_header("Content-Type",
                                "application/x-www-form-urlencoded")

        self.cookiejar.add_cookie_header(request)
        request.headers.update(request.unredirected_hdrs)
        return request

    def make_response(self, sock, req):
        """ 根据socket和urlib2.Request 构建Response """
        sock.setblocking(True)
        data = req.get_data()
        method = "POST" if data else "GET"
        r = httplib.HTTPResponse(sock, 0, strict = 0, method = method,
                                 buffering=True)
        r.begin()

        r.recv = r.read
        fp = socket._fileobject(r, close=True)

        resp = urllib.addinfourl(fp, r.msg, req.get_full_url())
        resp.code = r.status
        resp.msg = r.reason
        self.cookiejar.extract_cookies(resp, req)
        self.cookiejar.save()
        return resp


    def get_host(self, host):
        """ 根据域名获取ip """
        if self.host_map.has_key(host):
            return self.host_map[host]

        ip = socket.gethostbyname(host)
        if ip:
            #self.host_map[host] = ip
            return ip

        return host


    def make_http_sock_data(self, request, proxy = None):
        """ 根据urllib2.Request 构建socket和用于发送的HTTP源数据 """
        url = request.get_full_url()
        headers = request.headers
        data = request.get_data()
        parse = urlparse.urlparse(url)
        host, port = urllib.splitport(parse.netloc)
        typ = parse.scheme
        port = port if port else getattr(httplib, typ.upper() + "_PORT")
        data =  self.get_http_source(parse, data, headers, proxy)
        if hasattr(self, "do_" + typ):
            return getattr(self, "do_"+typ)(host, port, proxy), data

    def do_http(self, host, port, proxy = None):
        host = self.get_host(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        if proxy:
            host, port = proxy
        sock.connect((host, int(port)))
        sock.setblocking(0)
        return sock

    def do_https(self, host, port, proxy = None, keyfile = None, certfile = None):
        host = self.get_host(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        if proxy:
            host, port = proxy
        sock.connect((host, int(port)))
        sock = ssl.wrap_socket(sock, keyfile, certfile)
        sock.setblocking(0)
        return sock

    def get_http_source(self, parse, data, headers, proxy = None):
        path = parse.path
        query = parse.query
        path = path + "?" + query if query else path
        path = path if path else "/"
        method = "POST" if data else "GET"
        if proxy:
            path = "{0}://{1}{2}".format(parse.scheme, parse.netloc, path)
        _buffer= ["{0} {1} HTTP/1.1".format(method, path)]
        keys = [k.lower() for k in headers]
        e_headers = [(k.lower(), v) for k, v in headers.items()]
        headers = []
        headers.append(("Host", parse.netloc))
        if proxy:
            headers.append(("Proxy-Connection", "keep-alive"))
        else:
            'connection' not in keys and headers.append(("Connection",
                                                         "keep-alive"))

        'accept' not in keys and headers.append(("Accept", "*/*"))
        'accept-charset' not in keys and headers.append(("Accept-Charset",
                                                         "UTF-8,*;q=0.5"))
        'user-agent' not in keys and \
                headers.append(("User-Agent",
                                "Mozilla/5.0 (X11; Linux x86_64)"\
                                " AppleWebKit/537.11 (KHTML, like Gecko)"\
                                " Chrome/23.0.1271.97 Safari/537.11"))
        headers+= e_headers
        if data:
            headers.append(("Content-Length",   len(data)))

        for key, value in headers:
            _buffer.append("{0}: {1}".format(key.title(), value))

        _buffer.extend(("", ""))

        result = "\r\n".join(_buffer)
        if isinstance(data, str):
            result += data

        return result

    @property
    def cookie(self):
        return self.cookiejar._cookies


class TornadoHTTPClient(object):
    """ 基于Tornado的高效异步HTTP客户端类
    应当按照如下方法调用:
        http = TornadoHTTPClient.instance()
        def callback(resp):
            print resp.read()
            http.stop()

        http.get("http://www.badidu.com")
        http.get("http://www.baidu.com", callback = callback)
        http_stream.start()
    """
    ioloop = IOLoop.instance()
    http_sock = HTTPSock()
    cookie = http_sock.cookie
    cookiejar = http_sock.cookiejar
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.fd_map = {}
        self.fd_request_map = {}
        self.proxy = ()

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls(cls._ioloop, cls._http_sock)
        return cls._instance

    def set_proxy(self, host, port = 80):
        self.proxy = (host, int(port))

    def unset_proxy(self):
        self.proxy = ()

    def make_get_request(self, url, params = None):
        if params:
            url = self.make_get_url(url, params)
        return self.http_sock.make_request(url)

    def make_post_request(self, url, params):
        return self.http_sock.make_request(url, params)

    def make_get_url(self, url, params):
        return self.http_sock.make_get_url(url, params)

    def get(self, url, params = {}, headers = {}, callback = None,
            args = (), kwargs = {}, delay = 0):
        """ get方法请求HTTP
        Arguments:
            `url`       -   请求url
            `params`    -   请求参数
            `headers`   -   请求
            `callback`  -   读取response的函数,应接受一个response参数, 并且是第一个参数
            `args`      -   传递给callback的额外参数
            `kwargs`    -   传递给callback的额外参数
            `delay`     -   延迟请求, 单位为秒
        """
        self.request(self.make_get_request, url, params, headers, callback,
                     args, kwargs, delay)


    def post(self, url, params = {}, headers = {}, callback = None,
             args = (), kwargs = {}, delay = 0):
        """ post方法请求HTTP
        Arguments:
            `url`       -   请求url
            `params`    -   请求参数
            `headers`   -   请求
            `callback`  -   读取response的函数,应接受一个response参数, 并且是第一个参数
            `args`      -   传递给callback的额外参数
            `kwargs`    -   传递给callback的额外参数
            `delay`     -   延迟请求, 单位为秒
        """
        self.request(self.make_post_request, url, params, headers, callback,
                     args, kwargs, delay)


    def request(self, make_func, url, params, headers = {}, callback = None,
                args = (), kwargs = {}, delay = 0):
        """ 请求HTTP
        Arguments:
            `make_func` -   制造请求的函数
            `url`       -   请求url
            `params`    -   请求参数
            `headers`   -   请求
            `callback`  -   读取response的函数,应接受一个response参数, 并且是第一个参数
            `args`      -   传递给callback的额外参数
            `kwargs`    -   传递给callback的额外参数
            `delay`     -   延迟请求, 单位为秒
        """
        req = make_func(url, params)

        [req.add_header(key, value) for key, value in headers.items()]
        self.add_delay_request(req, callback, args, kwargs, delay)


    def add_request(self, request, callback = None, args = (), kwargs = {}):
        """ 往流里添加请求
        Arguments:
            `request`   -   urllib2.Request
            `callback`  -   回调函数
            `args`      -   传递给callback的额外参数
            `kwargs`    -   传递给callback的额外参数
        """
        if not isinstance(request, urllib2.Request):
            raise ValueError, "Not a invaid requset"

        logging.debug(u"Add reuqest {0} {1}".format(request.get_full_url(),
                                                    request.get_method()))
        try:
            sock, data = self.http_sock.make_http_sock_data(request, self.proxy)
        except socket.timeout, err:
            logging.warn(traceback.format_exc())
            return
        except socket.error, err:
            logging.warn(traceback.format_exc())
            logging.error("Make socket from request Error {0!r}".format(err))
            return

        fd = sock.fileno()
        self.fd_map[fd] = sock
        self.fd_request_map[fd] = request
        callback = partial(self._handle_events, request, data, callback, args,
                           kwargs)
        logging.debug("Add request handler to IOLoop")
        self.ioloop.add_handler(fd, callback, IOLoop.WRITE)


    def add_delay_request(self, request, callback, args = (), kwargs = {},
                          delay = 60):
        if not delay:
            return self.add_request(request, callback, args, kwargs)
        t = threading.Thread(target = self._add_delay_request,
                             args = (request, callback, args, kwargs, delay))
        t.setDaemon(True)
        t.start()

    def _add_delay_request(self, request, callback, args = (), kwargs = {},
                           delay = 60):
        if isinstance(threading.currentThread(), threading._MainThread):
            raise threading.ThreadError, "Can't run this function in _MainThread"

        time.sleep(delay)
        self.add_request(request, callback, args, kwargs)


    def _handle_events(self, request, data, callback, args, kwargs, fd, event):
        """ 用于处理Tornado事件
        Arguments:
            `request`   -   urllib.Request
            `data`      -   socket要写入的数据
            `callback`  -   读取函数
            `errback`   -   错误处理
            以上参数应当使用partial封装然后将此方法作为IOLoop.add_handler的callback
            `fd`        -   IOLoop传递 文件描述符
            `event`     -   IOLoop传递 tornado
        """
        s = self.fd_map[fd]

        if event & IOLoop.READ:
            logging.debug(u"Reuqest {0} {1} READABLE".format(
                request.get_full_url(), request.get_method()))
            try:
                resp = self.http_sock.make_response(s, request)
            except httplib.BadStatusLine:
                logging.warn(traceback.format_exc())
                self.ioloop.remove_handler(fd)
                return
            except Exception, err:
                logging.warn(traceback.format_exc())
                logging.error(u"Make response error {0!r}".format(err))
                self.ioloop.remove_handler(fd)
                s.close()
                del self.fd_map[fd]
                return

            try:
                args = callback(resp, *args, **kwargs)
            except Exception, err:
                logging.warn(traceback.format_exc())
                logging.error(u"Read response error {0!r}".format(err))
                self.ioloop.remove_handler(fd)
                del self.fd_map[fd]
                s.close()
                return

            s.setblocking(False)
            s.close()
            del self.fd_map[fd]
            self.ioloop.remove_handler(fd)

        if event & IOLoop.WRITE:
            logging.debug(u"Reuqest {0} {1} WRITABLE".format(
                request.get_full_url(), request.get_method()))
            s.sendall(data)
            if callback:
                self.ioloop.update_handler(fd, IOLoop.READ)
            else:
                self.ioloop.remove_handler(fd)
                s.close()
                del self.fd_map[fd]

        if event & IOLoop.ERROR:
            logging.warn(u"Reuqest {0} {1} ERROR".format(
                request.get_full_url(), request.get_method()))
            pass

    def start(self):
        self.ioloop.start()

    def stop(self):
        self.ioloop.stop()

if __name__ == "__main__":
    http = TornadoHTTPClient()
    def callback(resp):
        print resp.read()
        http.stop()

    http.get("http://www.linuxzen.com", callback = callback)
    http.start()

__author__ = "cold"
__version__ = 0.1
