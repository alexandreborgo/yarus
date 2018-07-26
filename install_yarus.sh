#!/bin/bash

sudo mkdir -p /var/log/yarus/tasks/
sudo mkdir -p /var/lib/yarus/
sudo mkdir -p /etc/yarus/
sudo cp ./etc/config_client.yml /etc/yarus/
sudo cp ./etc/config_engine.yml /etc/yarus/
sudo cp yarus-ansible-inventory.py /var/lib/yarus/
mysql -u yarus -p yarus < yarus.sql

python -m pip install -e common
python -m pip install -e engine
python -m pip install -e tasksmanager
