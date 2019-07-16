#!/usr/bin/env bash
wget https://raw.githubusercontent.com/nodesource/distributions/master/deb/setup_12.x
bash setup_12.x
apt-get install nodejs -yq
npm install