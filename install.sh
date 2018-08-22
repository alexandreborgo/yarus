
# create /opt/yarus and all sub directories
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

# copy configuration files
cp -f configuration/httpd.conf /etc/httpd/conf/
rm -f /etc/httpd/conf.d/*
cp -f configuration/yarus_engine.conf /etc/httpd/conf.d
cp -f configuration/yarus_webui.conf /etc/httpd/conf.d
cp -f configuration/*.wsgi /opt/yarus/www
cp -f configuration/*.yml /opt/yarus/etc
cp -f webui/yarus/webui/static/* /opt/yarus/www/static
cp -f yarus-ansible-inventory.py /opt/yarus/scripts
cp -f yarus-scheduler.py /opt/yarus/scripts
cp -f configuration/tasksmanager.service /etc/systemd/system/

# create Python3.6 venv for yarus
python3.6 -m venv /opt/yarus/env

# install yarus in the new venv
source /opt/yarus/env/bin/activate
python -m pip install --upgrade pip
python -m pip install ./common ./webui ./engine ./tasksmanager

# generate SSL certificat for apache
openssl req -x509 -nodes -days 1825 -newkey rsa:4096 -keyout /opt/yarus/cert/yarus_webui.key -out /opt/yarus/cert/yarus_webui.cert

# create the user yarus
useradd yarus
chown -R yarus:yarus /opt/yarus
chmod -R 755 /opt/yarus

# create all sql tables
mysql -u yarus -p yarus < yarus.sql
