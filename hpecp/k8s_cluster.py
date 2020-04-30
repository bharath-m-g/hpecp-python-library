from __future__ import absolute_import
from .logger import Logger

import json
from operator import attrgetter
from tabulate import tabulate
import polling
from enum import Enum

import sys
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str
else:
    string_types = basestring


class K8sClusterHostConfig():
    def __init__(self, node_id, node_role):
        assert isinstance(node_id, int), "'node_id' must be an int"
        assert node_role in [ 'master', 'worker' ], "'node_role' must one of ['master, worker']"

        self.node_id = node_id
        self.node_role = node_role

    def to_dict(self):
        return { 
                'node': '/api/v2/worker/k8shost/{}'.format(self.node_id), 
                'role': self.node_role 
            }
        
class K8sClusterController:

    def __init__(self, client):
        self.client = client

    def create(self, 
                name=None, 
                description=None, 
                k8s_version=None,
                pod_network_range='10.192.0.0/12', 
                service_network_range='10.96.0.0/12',
                pod_dns_domain='cluster.local',
                persistent_storage_local=False,
                persistent_storage_nimble_csi=False,
                k8shosts_config = [],
                ):
        """Send an API Request to create a K8S Cluster.

        Args:
            name: required, at least 1 characters
            description: defaults to empty string if not provided
            k8s_version: Kubernetes version to configure. If not specified defaults to the latest version as supported by the rpms.
            pod_network_range: Network range to be used for kubernetes pods. Defaults to 10.192.0.0/12
            service_network_range: Network range to be used for kubernetes services that are exposed with Cluster IP. Defaults to 10.96.0.0/12
            pod_dns_domain: DNS Domain to be used for kubernetes pods. Defaults to cluster.local
            persistent_storage_local: Enables local host storage to be available in the kubernetes cluster
            persistent_storage_nimble_csi: Installs the Nimble CSI plugin for Nimble storage to be available in the kubernetes cluster
            k8shosts_config: list of K8sClusterHostConfig objects

        Returns:
            int: The ID for the K8S Cluster
            
        Raises:
            Exception: TODO - describe

        """
        assert isinstance(name, string_types) and len(name) > 0,"'name' must be provided and must be a string"
        assert description is None or isinstance(description, string_types), "'description' must be a string"
        assert k8s_version is None or isinstance(k8s_version, string_types), "'k8s_version' must be a string"
        assert isinstance(pod_network_range, string_types), "'pod_network_range' must be a string"
        assert isinstance(service_network_range, string_types), "'service_network_range' must be a string"
        assert isinstance(pod_dns_domain, string_types), "'pod_dns_domain' must be a string"
        assert isinstance(persistent_storage_local, bool), "'persistent_storage_local' must be True or False"
        assert isinstance(persistent_storage_nimble_csi, bool), "'persistent_storage_nimble_csi' must be True or False"
        assert len(k8shosts_config) > 0, "'k8shosts_config' must have at least one item"
        for i, conf in enumerate(k8shosts_config):
            assert isinstance(conf, K8sClusterHostConfig), "'k8shosts_config' item '{}' is not of type K8sClusterHostConfig".format(i)

        data = {
            'label': { 
                'name': name
            },
            'pod_network_range': pod_network_range,
            'service_network_range': service_network_range,
            'pod_dns_domain': pod_dns_domain,
            'persistent_storage': { 
                'local': persistent_storage_local,
                'nimble_csi': persistent_storage_nimble_csi
            },
            'k8shosts_config': [ c.to_dict() for c in k8shosts_config ]
        }
        if description is not None: data['label']['description'] = description
        if k8s_version is not None: data['k8s_version'] = k8s_version

        response = self.client._request(url='/api/v2/k8scluster', http_method='post', data=data, description='k8s_cluster/create')
        return response.headers['Location'].split('/')[-1]

 