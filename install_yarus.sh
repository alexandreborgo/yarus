#!/bin/bash

mkdir -p /var/log/yarus/tasks/
mkdir -p /var/lib/yarus/
mkdir -p /etc/yarus/
cp ./etc/config_client.yml /etc/yarus/
cp ./etc/config_engine.yml /etc/yarus/
cp yarus-ansible-inventory.py /var/lib/yarus/

python -m pip install -e common
python -m pip install -e engine
python -m pip install -e tasksmanager
