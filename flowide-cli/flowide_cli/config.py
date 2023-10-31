import os

import dotenv

from python_on_whales import DockerClient
from fabric import Connection

CLOUD_DOCKERFILE = os.path.join(
    os.environ.get('FLOWIDE_DOCKER_DEPLOYMENT', '/root/docker-deployment'),
    'docker-compose.yml')

ENV_CONFIG_FILE = os.path.join((os.environ.get('FLOWIDE_DOCKER_DEPLOYMENT',
                                 '/root/docker-deployment')), '.env')

ENV_CONFIG = dotenv.dotenv_values(
    os.path.join((os.environ.get('FLOWIDE_DOCKER_DEPLOYMENT',
                                 '/root/docker-deployment')), '.env'))

NETWORK = 'workbench-network'

EDGE_DOCKERFILE = os.path.join(
    os.environ.get('FLOWIDE_DOCKER_DEPLOYMENT', '/root/docker-deployment'),
    'edge', 'docker-compose.yml')

EDGE_ENV_CONFIG_FILE = os.path.join(
                os.environ.get('FLOWIDE_DOCKER_DEPLOYMENT',
                               '/root/docker-deployment'), 'edge', '.env')

EDGE_ENV_CONFIG = dotenv.dotenv_values(
    os.path.join(
        os.environ.get('FLOWIDE_DOCKER_DEPLOYMENT', '/root/docker-deployment'),
        'edge', '.env'))

EDGE_NETWORK = F'{os.path.basename(os.path.dirname(EDGE_DOCKERFILE))}_deployment-edge'

CLOUD_VPN_ADDRESS = '10.181.240.11'
EDGE_VPN_ADDRESS = '10.181.240.10'

EDGE_USER = 'root'

__cloud_client: DockerClient = None
__edge_client: DockerClient = None


def get_cloud_docker_client() -> DockerClient:
    global __cloud_client

    if not __cloud_client:
        __cloud_client = DockerClient(compose_files=[CLOUD_DOCKERFILE])
    return __cloud_client


def get_edge_docker_client() -> DockerClient:
    global __edge_client

    if not __edge_client:
        __edge_client = DockerClient(
            host=f'ssh://{EDGE_USER}@{EDGE_VPN_ADDRESS}',
            compose_files=[EDGE_DOCKERFILE],
            compose_env_file=EDGE_ENV_CONFIG_FILE)
    return __edge_client


__edge_connection: Connection = None


def get_edge_connection() -> Connection:
    global __edge_connection

    if not __edge_connection:
        __edge_connection = Connection(EDGE_VPN_ADDRESS, user=EDGE_USER)
    return __edge_connection
