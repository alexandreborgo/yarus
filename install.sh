
mkdir /opt/yarus
mkdir /opt/yarus/etc
mkdir /opt/yarus/tmp
mkdir /opt/yarus/log
mkdir /opt/yarus/log/tasks
mkdir /opt/yarus/scripts
mkdir /opt/yarus/www
mkdir /opt/yarus/www/static
mkdir /opt/yarus/repositories
mkdir /opt/yarus/cert

cp configuration/httpd.conf /etc/httpd/conf/
rm -f /etc/httpd/conf.d/*
cp configuration/yarus_engine.conf /etc/httpd/conf.d
cp configuration/yarus_webui.conf /etc/httpd/conf.d
cp configuration/*.wsgi /opt/yarus/www
cp configuration/*.yml /opt/yarus/etc
cp webui/yarus/webui/static/* /opt/yarus/www/static
cp yarus-ansible-inventory.py /opt/yarus/scripts
cp yarus-scheduler.py /opt/yarus/scripts

python3.6 -m venv /opt/yarus/env

source /opt/yarus/env/bin/activate
python -m pip install --upgrade pip
python -m pip install ./common ./webui ./engine ./tasksmanager

openssl req -x509 -nodes -days 1825 -newkey rsa:4096 -keyout /opt/yarus/cert/yarus_webui.key -out /opt/yarus/cert/yarus_webui.cert

useradd yarus

chown -R yarus:yarus /opt/yarus
chmod -R 755 /opt/yarus

mysql -u yarus -p yarus < yarus.sql

systemctl start httpd.service
systemctl enable httpd.service

cp configuration/tasksmanager.service /etc/systemd/system/
