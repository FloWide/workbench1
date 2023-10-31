import typer
from .dockercommands import docker
from .cloud import cloud
from .edge import edge

app = typer.Typer()


app.add_typer(docker,name="docker")
app.add_typer(cloud,name="cloud")
app.add_typer(edge,name="edge")


def main():
    app()

if __name__ == "__main__":
    app()