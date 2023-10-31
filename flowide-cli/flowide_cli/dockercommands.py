import json
import os
import subprocess
from rich.console import Console
from rich.table import Table
from python_on_whales import ContainerStats, DockerClient
from typing import Dict, List, Optional, Callable, Any
from fabric import Connection

from . import config
import io
import typer


console = Console()

client: DockerClient = None
network_name: str = ''
is_edge: bool = False
edge_connection: Connection = None

docker = typer.Typer(name="docker")

@docker.callback()
def pre_callback(
    edge: bool = typer.Option(False)
):
    global client,network_name,is_edge,edge_connection
    client = config.get_edge_docker_client() if edge else config.get_cloud_docker_client()
    network_name = config.EDGE_NETWORK if edge else config.NETWORK
    is_edge = edge
    edge_connection = config.get_edge_connection() if edge else None

    if edge:
        if not os.path.exists(config.EDGE_ENV_CONFIG_FILE):
            console.print(f"[yellow]Warning: Edge config .env file not found: {config.EDGE_ENV_CONFIG_FILE}")
        if not os.path.exists(config.EDGE_DOCKERFILE):
            console.print(f"[yellow]Warning: Edge docker compose file not found: {config.EDGE_DOCKERFILE}")
    else:
        if not os.path.exists(config.ENV_CONFIG_FILE):
            console.print(f"[yellow]Warning: Cloud config .env file not found: {config.EDGE_ENV_CONFIG_FILE}")
        if not os.path.exists(config.CLOUD_DOCKERFILE):
            console.print(f"[yellow]Warning: Cloud docker compose file not found: {config.EDGE_DOCKERFILE}")


def run_shell_process(cmd: str):
    if not is_edge:
        subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            check=True
        )
    else:
        result = edge_connection.run(cmd,hide=True)
        if result.exited != 0:
            raise subprocess.CalledProcessError(result.exited,result.command,result.stdout,result.stderr)

def save_config(config: dict):
    if not is_edge:
        with open('/etc/docker/daemon.json','w') as f:
            json.dump(config,f)
    else:
        file_like = io.StringIO()
        json.dump(config,file_like)
        edge_connection.put(
            file_like,
            remote='/etc/docker/daemon.json'
        )
        file_like.close()

@docker.command()
def setup(
        data_root_path: Optional[str] = None,
        hosts: Optional[List[str]] = None
):
    with console.status('Updating apt cache...') as status:
        try:
            run_shell_process('apt-get update')
            status.update('Installing required packages...')
            run_shell_process('apt-get install -y ca-certificates curl gnupg lsb-release jq')
            status.update('Downloading docker gpg key...')
            run_shell_process('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg')
            status.update('Adding docker package repository...')
            run_shell_process('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null')
            status.update('Updating cache...')
            run_shell_process('apt-get update')
            status.update('Installing docker')
            run_shell_process('apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin')
            status.update('Setting docker config...')
            config = {
                    "log-driver":"json-file",
                    "log-opts":{
                        "max-size":"20m",
                        "max-file":"3"
                    }
            }
            if data_root_path:
                config.update({'data-root':data_root_path})

            if hosts:
                config.update({'hosts':hosts})
            save_config(config)
            status.update('Restarting docker...')
            run_shell_process('systemctl restart docker')
        except subprocess.CalledProcessError as e:
            console.print(e,style="red")
            console.print(e.stderr.decode())

@docker.command()
def recreate(services: Optional[List[str]] = typer.Argument(None)):
    if not services:
        client.compose.down()
        client.compose.up(force_recreate=True,detach=True)
    else:
        with console.status('Stopping services...') as status:
            client.compose.stop(services)
            status.update("Removing old containers...")
            client.compose.rm(services)
            status.update("Creating new containers...")
            client.compose.create(services)
            status.update("Starting services...")
            client.compose.start(services)
        console.print(f"[green]Recreated services: {','.join(services)}")

@docker.command()
def build(services: Optional[List[str]] = typer.Argument(None)):
    client.compose.build(services or None,cache=False)

@docker.command()
def restart(services: Optional[List[str]] = typer.Argument(None)):
    client.compose.restart(services or None)

@docker.command()
def up(services: Optional[List[str]] = typer.Argument(None)):
    client.compose.up(services or None,detach=True)

@docker.command()
def down():
    client.compose.down()

@docker.command()
def status():
    table = Table(title="Services",show_lines=True)

    table.add_column('Service')
    table.add_column('Status')
    table.add_column('IP address')
    table.add_column('Ports')

    for container in client.compose.ps(all=True):
        network = container.network_settings.networks.get(network_name)
        table.add_row(
            container.name,
            status_formatter(container.state),
            (network and network.ip_address) or 'N/A',
            port_formatter(container.network_settings.ports),
            style={
                "running":"green",
                "restarting":"yellow",
                "exited":"red",
                "created":"cyan"
            }.get(container.state.status)
        )

    console.print(table)

@docker.command()
def logs(
    services: List[str] = typer.Argument(None),
    tail: Optional[str] = None,
    follow: bool = False,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    generator = client.compose.logs(
                    services,
                    tail=tail,
                    follow=follow,
                    since=since,
                    until=until,
                    timestamps=True,
                    stream=True,
                    no_log_prefix=len(services) == 1
                )
    for source,content in generator:
        console.print(content.decode(),end="")

@docker.command()
def exec(
    container: str = typer.Argument(None),
    command: str = typer.Argument('bash')
):
    try:
        client.execute(
            container,
            command,
            interactive=True,
            tty=True
        )
    except Exception as e:
        console.print(f'[red]Container {container} doesn\'t exists')



def port_formatter(ports: Dict[str,List[Dict[str,str]]]):
    value = ""
    for port,binds in ports.items():
        if binds:
            for bind in binds:
                value += f"{port}->{bind['HostIp']}:{bind['HostPort']}\n"
        else:
            value += f"{port}\n"
    return value

def status_formatter(state: ContainerStats):
    value = f"{state.status}"
    if state.health:
        value += f" ({state.health.status})" 
    return value
