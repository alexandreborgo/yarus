Les systèmes
============

Informations requises
---------------------

Name

    Son nom (hostname).

Description

    Un description.

Adresse IP

    Son adresse IP.

Distribution

    Le nom de sa distribution

Version

    La version de la distribution.

Architecture

    Son architecture.

Type

    APT ou YUM.


Enregistrer un système
----------------------

Deux moyens sont disponibles pour enregistrer un système sur YARUS : manuellement ou automatiquement (exécution d'un script).

Manuellement
^^^^^^^^^^^^

.. warning::

    L'enregistrement manuel ne permet pas de configurer le système pour que YARUS puisse s'y connecter.

Pour enregistrer manuellement un système allez dans ``Systems`` et cliquez sur ``Add a system``.


Automatiquement
^^^^^^^^^^^^^^^

Le script config-system.py (python 2.7 et plus) permet de configurer et d'enregistrer un système sur un serveur YARUS.

Pour configurer le système le script doit être lancer avec les options ``--config`` et ``--server``.
Pour enregistrer le système le script doit être lancer avec les options ``--group``, ``--server``, ``-d``, ``-v``, ``-a`` et ``--ip``.

 * ``--group`` suivit de l'ID du group dans lequel le système sera placé (à chercher sur YARUS)
 * ``-d`` suivit de la distribution du système (debian, centos, ubuntu, rhel)
 * ``-v`` suivit de la version du système (stretch, bionic, 7.5, ...)
 * ``-a`` suivit de l'architecture du système (amd64, x86_64, ...)
 * ``--ip`` suivit de l'adresse IP du système (10.0.4.1, ...)

Pour Debian et Ubuntu les options ``-d``, ``-v`` et ``-a`` ne sont pas obligatoires.
Pour CentOS et RHEL les options ``-v`` et ``-a`` sont obligatoires sinon la version et l'architecture enregistrer sur le server YARUS ne seront pas bonnes.

Commandes pour configuer et enregistrer automatiquement les systèmes :

::

 $ python config-system.py --server ADRESSE_IP_SERVEUR_YARUS --config --group ID_DU_GROUPE -d DISTRIBUTION -v VERSION -a ARCHITECTURE --ip IP_CLIENT

Exemples :

 * Server YARUS :  10.0.2.42
 * Distribution :  debian 
 * Version :       stretch 
 * Architecture :  amd64
 * IP système :    10.0.2.1

::

$ python config-system.py --server 10.0.2.42 --config --group ID_DU_GROUPE -d debian -v stretch -a amd64 --ip 10.0.2.1

 * Server YARUS :  10.0.2.42
 * Distribution :  centos 
 * Version :       7.5 
 * Architecture :  x64
 * IP système :    10.0.2.1

::

 $ python config-system.py --server 10.0.2.42 --config --group ID_DU_GROUPE -d centos -v 7.5 -a x64 --ip 10.0.2.1

.. warning::

    Sans ces options (``-d``, ``-v``, ``-a`` et ``--ip``) le script essayera de récupérer ces informations sur le système.

    Cependant cette méthode n'est pas assez fiable (et pas du tout sur CentOS et RHEL) et est donc fortement déconseillée.

.. note::

    Le script nécessite Python 2.7.


Association avec des canaux
---------------------------

A son enregistrement le système sera automatiquement lié à un canal en fonction des règles d'associations.

Les canaux / dépôts associés au système peuvent être changer depuis la page d'un système dans les sections ``Repositories/Channels linked to the system`` 
(pour en supprimer) et ``Link repositories/channels to the system`` (pour en ajouter).


Liste des paquets à mettre à jour
---------------------------------

La tâche ``List of upgradable packages`` permet de récupérer la liste des paquets à mettre à jour. Un fois la tâche exécuter, la liste 
est disponible dans la section ``List of upgradable packages`` sur la page du système.

Depuis cette même section les paquets peuvent être approuvé ou désapprouvé pour la mise à jour.

.. note::

    Les paquets approuvés seront mis à jour lors de l'exécution de la tâche ``Update approved``.

.. warning::

    La tâche ``Update all`` mettra tous les paquets à jour, qu'ils soient approuvés ou non.


Mettre à jour le système
------------------------

Pour mettre à jour le système il faut exécuter une des deux tâches : ``Update approved`` ou ``Update all``.

La première tâche met à jour les paquets approuvés et la deuxième met tous les paquets à jour.


Historique des mises à jour
---------------------------

Dans la dernière section, ``Update history``, se trouve la liste des mises à jour effectuer sur le client.


Importer les paquets à approuver
--------------------------------

Pour approuver les paquets à mettre à jour sur un système, vous avez la possibilité de prendre la liste des paquets d'une mise à jour d'un autre système.

Par exemple : si vous avez deux systèmes, un système de test et un système de production. Vous pouvez approuver certains paquets sur le système de test et 
lancer la mise à jour avec la tâche ``Update approved``. Si vous décidez ensuite de mettre ces paquets à jour sur le systme en production vous
pouvez importer cette liste du système de test au système de production.

Pour faire cele cliquez sur l'action ``Import approved packages from an other client/group``. La liste des mises à jour des autres systèmes et groupe 
s'affichera et vous pourez choisir la mise à jour à importer.




