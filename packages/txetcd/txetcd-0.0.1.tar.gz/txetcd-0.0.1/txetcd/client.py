"""
Copyright 2013 Russell Haering.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import random

from dateutil.parser import parse as parse_datetime
from twisted.python import log

from treq import json_content
from treq.client import HTTPClient


class EtcdResponse(object):
    def __init__(self, **kwargs):
        self.action = kwargs.get('action')
        self.key = kwargs.get('key')
        self.value = kwargs.get('value')
        self.index = kwargs.get('index')
        self.new_key = kwargs.get('newKey')
        self.prev_value = kwargs.get('prevValue')
        self.expiration = kwargs.get('expiration')
        if self.expiration:
            self.expiration = parse_datetime(self.expiration)


class EtcdError(Exception):
    def __init__(self, **kwargs):
        super(EtcdError, self).__init__(kwargs)
        self.code = kwargs.get('errorCode')
        self.message = kwargs.get('message')
        self.cause = kwargs.get('cause')


class EtcdClient(object):
    API_VERSION = 'v1'

    def __init__(self, seeds=[('localhost', 4001)]):
        self.nodes = set(seeds)
        self.http_client = HTTPClient.with_config()

    def _get_node(self, prefer_leader=False):
        # TODO: discover the rest of the cluster
        # TODO: cache the leader
        return random.sample(self.nodes, 1)[0]

    def _decode_response(self, response):
        return json_content(response).addCallback(self._construct_response_object)

    def _construct_response_object(self, obj):
        if 'errorCode' in obj:
            raise EtcdError(**obj)
        elif isinstance(obj, list):
            return [EtcdResponse(**item) for item in obj]
        else:
            return EtcdResponse(**obj)

    def _log_failure(self, failure):
        log.err(failure)
        return failure

    def _request(self, method, path, params=None, prefer_leader=False):
        node = self._get_node(prefer_leader=prefer_leader)
        url = 'http://{host}:{port}/{version}{path}'.format(
            host=node[0],
            port=node[1],
            version=self.API_VERSION,
            path=path,
        )
        return self.http_client.request(method, url, params=params).addErrback(self._log_failure)

    def set(self, key, value, prev_value=None, ttl=None):
        path = '/keys/{key}'.format(key=key)
        params = {'value': value}

        if ttl is not None:
            params['ttl'] = ttl

        if prev_value is not None:
            params['prevValue'] = prev_value

        d = self._request('POST', path, params=params, prefer_leader=True)
        return d.addCallback(self._decode_response)

    def delete(self, key):
        path = '/keys/{key}'.format(key=key)
        d = self._request('DELETE', path, prefer_leader=True)
        return d.addCallback(self._decode_response)

    def get(self, key):
        path = '/keys/{key}'.format(key=key)
        d = self._request('GET', path)
        return d.addCallback(self._decode_response)

    def watch(self, key, index=None):
        path = '/watch/{key}'.format(key=key)
        params = {}

        if index is not None:
            params['index'] = index

        d = self._request('GET', path, params=params)
        return d.addCallback(self._decode_response)

