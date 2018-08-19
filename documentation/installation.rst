Installation
============

yum update -y 

yum groupinstall development

yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel make wget 

yum-utils
yum-builddep python

wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tar.xz

tar xf Python-3.6.6.tar.xz

cd Python-3.6.6

./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"

make 

make altinstall

python 

python3.6 -m pip install mod_wsgi

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

systemctl start httpd.service
systemctl restart httpd.service
systemctl reload httpd.service
systemctl enable httpd.service

MySQL:
CREATE DATABASE yarus;
CREATE USER 'yarus'@'localhost' IDENTIFIED BY 'fN8enm*5s~4}dPDK';
GRANT ALL PRIVILEGES ON yarus.* TO 'yarus'@'localhost';
FLUSH PRIVILEGES;

systemctl restart mysql.service
systemctl enable mysql.service