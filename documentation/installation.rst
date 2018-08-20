Installation
============

Partitionnement du système
/ 10 GiO
/home 1 GiO
/boot 1 GiO
/opt beaucoup

Confirguration
systemctl stop firewalld
setenforce 0

Ports ouverts:
- 443
- 6128

yum update -y 

Python 3.6 installation:

    yum groupinstall development
    yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel make wget 
    wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tar.xz
    tar xf Python-3.6.6.tar.xz
    cd Python-3.6.6
    ./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
    make
    make altinstall
    python3.6
    exit()
    python3.6 -m pip install --upgrade pip
    make clean
    cd ..

Apache HTTP Server 2.4 et le module WSGI:

    yum install -y httpd httpd-devel mod_ssl
    python3.6 -m pip install mod_wsgi

MySQL 8.0

    wget https://dev.mysql.com/get/mysql80-community-release-el7-1.noarch.rpm
    rpm -ivh mysql80-community-release-el7-1.noarch.rpm
    yum install -y mysql-community-server
    systemctl start mysqld.service
    systemctl enable mysqld.service
    systemctl status mysqld.service
    grep 'temporary password' /var/log/mysqld.log
    mysql -u root -p
    ALTER USER 'root'@'localhost' IDENTIFIED BY '1tx;oKqH3yhk1tx;oKqH3yhk';
    CREATE DATABASE yarus;
    CREATE USER 'yarus'@'localhost' IDENTIFIED BY 'fN8enm*5s~4}dPDK';
    GRANT ALL PRIVILEGES ON yarus.* TO 'yarus'@'localhost';
    FLUSH PRIVILEGES;

Install YARUS:
    yum install -y ansible rsync
    git clone https://github.com/alexandreborgo/yarus
    cd yarus
    chmod +x install.sh
    ./install.sh
