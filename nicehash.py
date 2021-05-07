import config
from datetime import datetime
from time import mktime
import uuid
import hmac
import requests
import json
from hashlib import sha256
import optparse
import sys


class public_api:

    def __init__(self, verbose=False):
        self.host = config.HOST
        self.verbose = verbose

    def request(self, method, path, query, body):
        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        s = requests.Session()
        if body:
            body_json = json.dumps(body)
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_current_prices(self):
        return self.request('GET', '/exchange/api/v2/info/prices', '', None)

class private_api:

    def __init__(self, verbose=False):
        self.key = config.KEY
        self.secret = config.SECRET
        self.organisation_id = config.ORGANISATION_ID
        self.host = config.HOST
        self.verbose = verbose

    def request(self, method, path, query, body):

        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = bytearray(self.key, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(str(xtime), 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(xnonce, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(self.organisation_id, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(method, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(path, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(query, 'utf-8')

        if body:
            body_json = json.dumps(body)
            message += bytearray('\x00', 'utf-8')
            message += bytearray(body_json, 'utf-8')

        digest = hmac.new(bytearray(self.secret, 'utf-8'), message, sha256).hexdigest()
        xauth = self.key + ":" + digest

        headers = {
            'X-Time': str(xtime),
            'X-Nonce': xnonce,
            'X-Auth': xauth,
            'Content-Type': 'application/json',
            'X-Organization-Id': self.organisation_id,
            'X-Request-Id': str(uuid.uuid4())
        }

        s = requests.Session()
        s.headers = headers

        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        if body:
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

    def get_accounts(self):
        return self.request('GET', '/main/api/v2/accounting/accounts2/', '', None)
    
    def get_accounts_for_currency(self, currency):
        return self.request('GET', '/main/api/v2/accounting/account2/' + currency, '', None)

    def get_rigs(self):
        return self.request('GET', '/main/api/v2/mining/rigs2', '', None)


# def build_request(endpoint, params):

#     xtime = get_epoch_ms_from_now(self)

#     key = config.KEY
#     secret = config.SECRET
#     organisation_id = config.ORGANISATION_ID
#     method = "GET"

#     path = endpoint
#     query = params

#     xnonce = str(uuid.uuid4())

#     message = bytearray(key, 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray(str(xtime), 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray(xnonce, 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray(organisation_id, 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray(method, 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray(path, 'utf-8')
#     message += bytearray('\x00', 'utf-8')
#     message += bytearray(query, 'utf-8')

#     digest = hmac.new(bytearray(secret, 'utf-8'), message, sha256).hexdigest()
#     xauth = key + ":" + digest

#     url = "https://api2.nicehash.com" + path + "?" + query

#     response = requests.get(url, 
#                             headers = {
#                                 'X-Time': str(xtime),
#                                 'X-Nonce': xnonce,
#                                 'X-Auth': xauth,
#                                 'Content-Type': 'application/json',
#                                 'X-Organization-Id': organisation_id,
#                                 'X-Request-Id': str(uuid.uuid4())
#                             }
#                             )
#     return json.loads(response.text)