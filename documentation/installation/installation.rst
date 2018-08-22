Installation
============

YARUS est divisé en trois composant.

Engine
    Une API RESTful qui permet de contrôler le système.

Webui
    Une interface web pour l'utilisateur.

Task Manager
    Le service qui éxécute les tâches de synchronisation, de configuration, de mise à jour...

.. warning::

    Ces trois composants doivent être installés sur le même serveur.

    La base de données MySQL devra aussi être installé sur ce même server

Plateformes supportées
----------------------

YARUS peut être installé sur n'importe quel système qui supporte Python 3.6 et supérieur ainsi que ses dépendances : Apache HTTP Server, MySQL Community Server, Ansible, Rsync et systemd.

YARUS a été développé sur CentOS 7.5 et a été testé avec succès sur CentOS 7.5.

Prérequis
---------

Partitionnement du système
^^^^^^^^^^^^^^^^^^^^^^^^^^

YARUS s'intallera dans le dossier ``/opt/yarus``. C'est dans des sous répertoires de cet emplacement que les dépôts seront clonés et que la base de données sera sauvegardée.

Quelques exemples sur l'espace nécéssaire pour la copie de dépôts YUM et APT :

* 62G pour CentOS 5.11 (tous)
* 80G pour CentOS 6.9 (tous)
* 86G pour CentOS 7.5 (tous)
* 

Vous devez donc attribuer un espace en fonction du nombre de dépôt que vous souhaitez récupérer.


Ports nécéssaires
^^^^^^^^^^^^^^^^^

Par défaut les ports utilisés par YARUS Engine et YARUS Webui sont :

* 443 Apache HTTP Server pour la Webui
* 6128 Apache HTTP Server pour l'Engine

Il est donc requis d'ouvrir les ports du système. Par exemple pour ``firewalld``::
    
    $ sudo firewall-cmd --permanent --add-port=443/tcp
    $ sudo firewall-cmd --permanent --add-port=6128/tcp
    $ sudo firewall-cmd --reload

Et de désactiver SELinux ::

    $ sudo setenforce 0

Instructions
------------

.. toctree::
    :maxdepth: 2

    instructionscr7
