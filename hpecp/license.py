from __future__ import absolute_import

from .logger import Logger

from datetime import datetime, timedelta
import time
import requests 
import json
import urllib

class LicenseController:

    def __init__(self, client):
        self.client = client

    def platform_id(self):
        response = self.client._request(url='/api/v1/license', http_method='get', description='license/get_platform_id')
        return response.json()['uuid']

    def list(self):
        response = self.client._request(url='/api/v2/hpelicense', http_method='get', description='license/get_license')
        return response.json()

    def upload(self, base64enc_license):
        """Not implemented yet!"""
        raise Exception("Not implemented yet!")  

    def register(self, server_filename):
        data = { "hpelicense_file": server_filename }
        response = self.client._request(url='/api/v2/hpelicense', http_method='post', data=data, description='license/register')
        return response

    def delete(self, license_key):
        try:
            lic = urllib.parse.quote(license_key)  # python 2
        except:
            lic = urllib.pathname2url(license_key) # python 3

        response = self.client._request(url='/api/v2/hpelicense/{}/'.format(lic), http_method='delete', description='license/delete')
        return response

