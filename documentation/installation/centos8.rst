Instructions pour CentOS 8 
==========================

Créer un répertoire pour l'installation ::

    $ mkdir yarus
    $ cd yarus

Mettre à jour le système
------------------------

Mettre à jour le système ::

    $ sudo yum update -y

Paquêts nécéssaires
-------------------

Les commandes suivantes installeront les paquêts nécéssaire à l'installation de Yarus ::

    $ sudo yum groupinstall -y development
    $ sudo yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel xz-devel expat-devel make wget redhat-rpm-config python3-devel

Apache HTTP Server
------------------

Le serveur HTTP est nécessaire pour servire l'Engine et la Webui ainsi que les dépôts. ::

    $ sudo yum install -y httpd httpd-devel mod_ssl

.. note::

    Le paquêt httpd-devel est nécessaire pour compiler mod_wsgi

Le module mod_wsgi permet à Apache de servir des applications web en Python. 
Le module doit être compiler avec un interpréteur Python de même version que les scripts qu'il éxecutera (ici 3.6).

Installer mod_wsgi avec Pypi permet d'obtenir la bonne version de l'interpréteur Python ::

    $ sudo python3.6 -m pip install mod_wsgi

.. note::

    Le serveur HTTP sera configuré et démarré dans la suite de l'installation


MySQL Server
------------

YARUS utilise un base de données MySQL 8 pour stocker ses données.

.. note::

    Les instructions suivantes proviennent de la documentation de l'installation de MySQL Server 8 accessible via le lien suivant : https://dev.mysql.com/doc/refman/8.0/en/linux-installation-yum-repo.html

Installer les dépôts de MySQL::

    $ wget https://dev.mysql.com/get/mysql80-community-release-el8-1.noarch.rpm
    $ sudo yum localinstall mysql80-community-release-el8-1.noarch.rpm 

Disable les dépôts MySQL qui ne sont pas les dépôts officiels ::

    $ sudo yum module disable mysql -y

Installer MySQL Server::

    $ sudo yum install -y mysql-community-server

Démarrer le serveur MySQL::

    $ systemctl start mysqld.service
    $ systemctl enable mysqld.service
    $ systemctl status mysqld.service

Lors de son installation MySQL a généré un mot de passe temporaire pour accéder à la base de données avec l'utilisateur root. Pour récupérer le mot de passe::

    $ grep 'temporary password' /var/log/mysqld.log

Connecter vous au serveur MySQL avec root et le mot de passe récupéré::

    $ mysql -u root -p

Changer le mot de passe root à l'aide de la commande suivante::

    mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_root';

.. warning::

    Aucune action n'est possible dans MySQL avant le changement du mot de passe root.

Nous devons maintenant créer un utilisateur et une base de données que YARUS pourra utiliser::

    mysql> CREATE DATABASE yarus;
    mysql> CREATE USER 'yarus'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_yarus';
    mysql> GRANT ALL PRIVILEGES ON yarus.* TO 'yarus'@'localhost';
    mysql> FLUSH PRIVILEGES;
    mysql> exit

YARUS
-----


Installer les dernières dépendances de YARUS::

    $ yum install -y ansible rsync git

.. note::

    Ansible n'est plus disponible dans les dépôts de CentOS8 pour le moment. Il est disponible dans les dépôts EPEL8 (https://fedoraproject.org/wiki/EPEL).
    Pour installer le dépôt rapidement utiliser la commande suivante::
	$ yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

Télécharger les sources de YARUS::

    $ git clone https://github.com/alexandreborgo/yarus

Exécuter le script d'installation de YARUS::

    $ cd yarus
    $ chmod +x yarus-install.sh
    $ sudo ./yarus-install.sh

.. warning::

    Le script demandera plusieurs informations pour terminer la configuration.

Configurer YARUS

    Aller dans le fichier de configuration `/opt/yarus/etc/engine.yml` pour y ajouter les informations suivantes

    * le mot de passe de l'utilisateur yarus de la base de données
    * l'addresse IP sur laquelle Yarus va être contacter par ses clients
    * les informations relatives au proxy si YARUS doit passer par un proxy pour la synchronisation des paquets
    
        * host : l'adresse du proxy
        * port : le port 
        * username : l'utilisateur 
        * password : le mot de passe
    
.. note::

    Laissez les champs vides si vous n'utilisez pas de proxy pour accéder à internet.

Démarer le serveur Apache::

    $ systemctl start httpd.service
    $ systemctl enable httpd.service
    $ systemctl status httpd.service

Vérifier que le service HTTPD a bien démarré.

Démarer YARUS Task Manager::

    $ systemctl start yarustaskmanager.service
    $ systemctl enable yarustaskmanager.service
    $ systemctl status yarustaskmanager.service

Vérifier que le service HTTPD a bien démarré.
