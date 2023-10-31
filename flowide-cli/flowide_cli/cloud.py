from typing import Optional
from pyroute2 import IPRoute, NDB
import requests
import typer
from . import config
from rich.console import Console
import subprocess

console = Console()

cloud = typer.Typer(name='cloud')



INTERFACE_PREFIX='veth-flowide-'

@cloud.command()
def create_port_forward(
        name: str,
        cloud_ip: str,
        edge_port: int,
        cloud_port: int = 80,
):
    ipr = IPRoute()
    ipr.link("add", ifname=f"veth0{name}", kind="dummy")

    # Add the interface to the Docker bridge
    ndb = NDB(log="on")
    ndb.interfaces[f"veth0{name}"].set("master", ndb.interfaces["docker0"])

    # Configure the IP address of the interface
    ipr.addr("add", index=ipr.link_lookup(ifname=f"veth0{name}")[0], address=cloud_ip, mask=32)

    # Configure the iptables rules
    subprocess.run(
        f"iptables -A PREROUTING -t nat -p tcp -d {cloud_ip} --dport {cloud_port} -j DNAT --to-destination {config.EDGE_VPN_ADDRESS}:{edge_port}",
        shell=True,
        check=True
    )
    subprocess.run(
        f"iptables -A POSTROUTING -t nat -p tcp -d {config.EDGE_VPN_ADDRESS} --dport {cloud_port} -j MASQUERADE",
        shell=True,
        check=True
    )
    subprocess.run(
        f"iptables -A FORWARD -p tcp -d {config.EDGE_VPN_ADDRESS} --dport {cloud_port} -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT",
        shell=True,
        check=True
    )
    


@cloud.command()
def apps_admin_install(
    name: str = "appInstaller",
    from_url: str = "https://github.com/FloWide-Apps/appInstaller.git",
    ref: str = 'refs/heads/master',
    oauth_token: Optional[str] = None
):
    with console.status("Getting access token...") as status:
        resp = requests.post(
            f"https://{config.ENV_CONFIG['SERVER']}-gw.{config.ENV_CONFIG['DOMAIN']}/auth/realms/{config.ENV_CONFIG['SERVER']}-gw/protocol/openid-connect/token",
            data={
                'client_id':'flowide-workbench',
                'username':'apps-admin',
                'password':config.ENV_CONFIG['APPS_ADMIN_PASSWORD'],
                'grant_type':'password'
            }
        ).json()
        token = resp["access_token"]
        status.update('Importing application...')
        data = {
                "name":name,
                "template":"streamlit",
                "from_url":from_url,
                "ref":ref
        }
        if oauth_token:
            data.update({"oauth_token":oauth_token})
        resp = requests.post(
            f"https://{config.ENV_CONFIG['SERVER']}-gw.{config.ENV_CONFIG['DOMAIN']}/workbench-api/repo/import",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type':'application/json'
            },
            json=data
        )
    if resp.status_code > 300:
        console.print(resp.text,style='red')
    else:
        console.print("Installed application...",style="green")
