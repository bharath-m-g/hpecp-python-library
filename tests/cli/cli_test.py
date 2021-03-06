from unittest import TestCase
from mock import Mock, patch, mock_open

from textwrap import dedent
import sys
import tempfile
import os
import json
import requests
from requests.exceptions import RequestException

sys.path.insert(0, os.path.abspath("../../"))
from bin import cli


class MockResponse:
    def __init__(
        self,
        json_data,
        status_code,
        headers,
        raise_for_status_flag=False,
        text_data="",
    ):
        self.json_data = json_data
        self.text = text_data
        self.status_code = status_code
        self.raise_for_status_flag = raise_for_status_flag
        self.headers = headers

    def raise_for_status(self):
        if self.raise_for_status_flag:
            self.text = "some error occurred"
            raise requests.exceptions.HTTPError()
        else:
            return

    def json(self):
        return self.json_data


class TestCLI(TestCase):

    # pylint: disable=no-method-argument
    def mocked_requests_post(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/login":
            return MockResponse(
                json_data={},
                status_code=200,
                headers={
                    "location": "/api/v1/session/df1bfacb-xxxx-xxxx-xxxx-c8f57d8f3c71"
                },
            )
        raise RuntimeError("Unhandle POST request: " + args[0])

    # pylint: disable=no-method-argument
    def mocked_requests_get(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v2/k8scluster":
            return MockResponse(
                json_data={
                    "_links": {"self": {"href": "/api/v2/k8scluster"}},
                    "_embedded": {
                        "k8sclusters": [
                            {
                                "_links": {
                                    "self": {"href": "/api/v2/k8scluster/20"}
                                },
                                "label": {
                                    "name": "def",
                                    "description": "my cluster",
                                },
                                "k8s_version": "1.17.0",
                                "pod_network_range": "10.192.0.0/12",
                                "service_network_range": "10.96.0.0/12",
                                "pod_dns_domain": "cluster.local",
                                "created_by_user_id": "/api/v1/user/5",
                                "created_by_user_name": "admin",
                                "created_time": 1588260014,
                                "k8shosts_config": [
                                    {
                                        "node": "/api/v2/worker/k8shost/4",
                                        "role": "worker",
                                    },
                                    {
                                        "node": "/api/v2/worker/k8shost/5",
                                        "role": "master",
                                    },
                                ],
                                "status": "ready",
                                "status_message": "really ready",
                                "api_endpoint_access": "api:1234",
                                "dashboard_endpoint_access": "dashboard:1234",
                                "admin_kube_config": "xyz==",
                                "dashboard_token": "abc==",
                                "persistent_storage": {"nimble_csi": False},
                            }
                        ]
                    },
                },
                status_code=200,
                headers={},
            )
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_example(self, mock_post, mock_get):

        file_data = dedent(
            """[default]
                        api_host = 127.0.0.1
                        api_port = 8080
                        use_ssl = True
                        verify_ssl = False
                        warn_ssl = True
                        username = admin
                        password = admin123"""
        )

        tmp = tempfile.NamedTemporaryFile(delete=True)
        try:
            tmp.write(file_data.encode("utf-8"))
            tmp.flush()

            cli.HPECP_CONFIG_FILE = tmp.name

            hpecp = cli.CLI()
            hpecp.k8scluster.list()

            self.assertTrue(True)

        finally:
            tmp.close()
