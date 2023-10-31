import setuptools


setuptools.setup(
    name="flowide_cli",
    version="0.0.1",
    author="FloWide Ltd.",
    description="Command line tool for deployment",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.8",
    install_requires=[
        "typer",
        "python-on-whales",
        "fabric",
        "python-dotenv",
        "rich",
        "pyroute2",
        "patchwork==1.0.1",
        "pyyaml"
    ],
    entry_points={"console_scripts": ["flowide=flowide_cli.__main__:main"]},

)