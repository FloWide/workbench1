#!/bin/bash


pip install ./flowide-cli
rm -rf ./flowide-cli/build
rm -rf ./flowide-cli/flowide_cli.egg-info

bashrc_extra="
if [ -f ~/.flowide ]; then
    source ~/.flowide
fi
"
grep -qxF "$bashrc_extra" ~/.bashrc || echo $bashrc_extra >> ~/.bashrc


echo "export FLOWIDE_DOCKER_DEPLOYMENT=$(pwd)" >> ~/.flowide
