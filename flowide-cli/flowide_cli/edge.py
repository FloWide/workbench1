import typer
from . import config
from patchwork.transfers import rsync
import os
from rich.console import Console
from rich.table import Table
import requests
import yaml

edge = typer.Typer(name='edge')
console = Console()

conn = config.get_edge_connection()
docker = config.get_edge_docker_client()


def username_to_userid(username: str):
    resp = requests.post(
            f"http://10.20.20.11/auth/realms/{config.ENV_CONFIG['SERVER']}-gw/protocol/openid-connect/token",
            data={
                'client_id':'flowide-workbench',
                'username':'apps-admin',
                'password':config.ENV_CONFIG['APPS_ADMIN_PASSWORD'],
                'grant_type':'password'
            }
        ).json()
    token = resp["access_token"]
    resp = requests.get(
        f"http://10.20.20.17/user",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type':'application/json'
        }
    )
    for id,user in resp.json().items():
        if user["username"] == username:
            return id
    return None


@edge.command()
def create_service(
    name: str,
    username: str,
    repo: str,
    script: str,
    version: str
):
    with console.status("Resolving username to userid..."):
        user_id = username_to_userid(username)
    
    if not user_id:
        console.print("[red]Couldn't resolve username")
        raise typer.Abort
    path_to_repo = os.path.join(
        config.ENV_CONFIG["SCRIPT_HANDLER_HOME"],
        'releases',
        user_id,
        repo,
        version
    )
    if not os.path.exists(path_to_repo):
        console.print(f'[red]Path doesn\'t exists: {path_to_repo}')
        raise typer.Abort()
    with open(os.path.join(path_to_repo,'appconfig.yml')) as f:
        appconfig = yaml.full_load(f)
    
    if script not in appconfig["apps"].keys():
        console.print(f"[red]Script {script} doesn't exists in release {repo}/{version}")
        raise typer.Abort()
    app = appconfig["apps"][script]

    with console.status('Copying files to edge...'):
        conn.run(f'mkdir -p services/{name}')
        rsync(
            conn,
            path_to_repo + "/",
            f'services/{name}',
            exclude='.git',
            delete=True
            
        )
    
    console.print("[green]Copied files")
    # docker run -it --rm --network=edge_deployment-edge --dns="127.0.0.11" --volume="/home/bgorzsony/test.py:/mnt/workdir/test.py" --workdir="/mnt/workdir" script_runner python test.py
    with console.status("Starting service..."):
        container = docker.run(
            image='script_runner',
            name=name,
            remove=True,
            networks=["edge_deployment-edge"],
            dns=["127.0.0.11"],
            volumes=[(f"/root/services/{name}","/mnt/workdir")],
            workdir="/mnt/workdir",
            command=[ *['python',app["config"]["entry_file"]], *app["config"]["cli_args"]],
            envs=app["config"]["env"],
            detach=True
        )
    console.print(f"[green]Started container with command {container.config.cmd}")

@edge.command()
def list_service():
    table = Table(title="Services",show_lines=True)

    table.add_column('Service')
    table.add_column('Status')

    with console.status("Getting services..."):
        for container in docker.compose.ps(all=True):
            if not container.config.image == 'script_runner' or container.name == 'script_runner':
                continue
            table.add_row(
                container.name,
                container.state.status,
                style={
                    "running":"green",
                    "restarting":"yellow",
                    "exited":"red",
                    "created":"cyan"
                }.get(container.state.status)
            )

    console.print(table)
@edge.command()
def delete_service(name: str):
    try:
        with console.status("Removing service..."):
            docker.remove(name,force=True)
    except Exception as e:
        console.print(e)