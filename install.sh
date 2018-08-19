cp configuration/httpd.conf /etc/httpd/conf/

mkdir -p /etc/yarus/
mkdir -p /var/log/yarus/
mkdir -p /var/lib/yarus/
mkdir -p /var/www/yarus/

cp configuration/yarus_engine.conf /etc/httpd/conf.d
cp configuration/yarus_webui.conf /etc/httpd/conf.d
cp configuration/*.wsgi /var/www/yarus
cp configuration/*.yml /etc/yarus

python3.6 -m venv /var/lib/yarus/env


source /var/lib/yarus/env/bin/activate
python -m pip install --upgrade pip
python -m pip install ./common ./webui ./engine

useradd yarus

chown -R yarus:yarus /var/lib/yarus
chown -R yarus:yarus /var/www/yarus
chown -R yarus:yarus /var/log/yarus

chmod -R 755 /var/www/yarus

systemctl start httpd
systemctl restart httpd
systemctl reload httpd
systemctl enable httpd

# sudo cp ./etc/webui.yml /etc/yarus/
# sudo cp ./etc/engine.yml /etc/yarus/
# sudo cp yarus-ansible-inventory.py /var/lib/yarus/
# sudo cp yarus-scheduler.py /var/lib/yarus/
# mysql -u yarus -p yarus < yarus.sql

# python -m pip install -e common
# python -m pip install -e engine
# python -m pip install -e tasksmanager
