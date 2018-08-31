Les dépôts
==========

Enregistrer un dépôt dans YARUS permettra de récupérer les paquets qu'il contient et de les rendre disponible pour les systèmes.

Informations requises
---------------------

Plusieurs informations sont nécessaires pour que YARUS puisse récupérer un dépôts YUM ou APT.

.. note::

    Des exemples seront donnés dans les sous parties `Ajouter un dépôts APT` et `Ajouter un dépôts YUM`.

Le type
    
    Le type du dépôt. Deux types sont pris en charge par YARUS : YUM et APT. Les dépôts YUM contiennent des paquets RPM utilisable par les distributions 
    Fedora et ses dérivées (Red Hat Enterprise Linux, CentOS...), les dépôts APT contiennent des paquets DEB utilisable par les distributions 
    Debian et ses dérivées (Ubuntu, Kali Linux...). 

L'URL
    
    L'adresse HTTP ou se situe la racine du dépôt. La racine est du dépôts est différente dans les deux types de dépôts.
    Pour YUM le répertoire parent du dossier ``repodata``. Et pour APT, le répertoire parent des répertoires ``dist`` (qui contient les métadonnées) 
    et ``pool`` (qui contient les packages).

La distribution / le logiciel

    Le nom de la distribution ou le nom du logiciel que représente le dépôt. Par exemple : centos, mysql, debian, ubuntu, postgresql.

La version

    La version de la distribution / du logiciel : stretch, bionic, 7.5.1804, 10...

.. warning::

    Pour CentOS on utilisera ici la version "numérique" : 6.5, 7.5.1804... Alors que pour Debian et Ubuntu il faut utiliser le nom de la version. 
    Car les dépôts sont organisés en fonction des noms et non des numéros. 

L'architecture

    L'architecture ciblée . Par exemple : i386, x86_64, amd64...

.. note::

    Pour les dépôts APT vous pouvez donner plusieurs architectures par dépôts. Il suffit de les séparer par une virgule comme ici : amd64,i386.

Le path

    Le chemin du dépôt. On y trouve des fichiers de métadonnées nécessaires à APT. C'est le nom du répertoire que l'on veut récupérer dans 
    le dossier ``dists`` sous la racine du dépôt. Par exemple : bionic-security, debian-update, debian/security...

.. warning::

    Seulement pour les dépôts APT.

Les composants

    Les composants du dépôts à récupérer. Par exemple : main, contrib, non-free...

.. warning::

    Seulement pour les dépôts APT.

.. note::

    Vous pouvez donner plusieurs composants par dépôts. Il suffit de les séparer par une virgule comme ici : main,contrib,non-free.


Ajouter un dépôts APT
---------------------

Nous souhaitons faire un miroir du dépôt de Ubuntu Bionic depuis le site distrib-coffee.ipsl.jussieu.fr

Le type

    APT

L'URL racine

    http://distrib-coffee.ipsl.jussieu.fr/pub/linux/ubuntu/.
    C'est sous ce répertoire que l'on trouve les dossiers ``dists`` et ``pool``.

La distribution

    Le nom de la distribution, ici : ubuntu.

La version

    La version est ici : bionic.

L'architecture

    Nous souhaitons seulement prendre les architectures 32 et 64 bits : amd64,i386.

Le path

    Nous souhaitons le chemin de base qui s'appelle ici : bionic.

Les composants

    Nous souhaitons tous les composants pour avoir tout le dépôt : main,multiverse,restricted,universe.

.. note::

    Pour cloner l'ensemble de l'archive de Ubuntu Bionic il faudra donc créer un dépôt pour chaque chemin 
    (bionic, bionic-updates, bionic-backports et bionic-security).

Ajouter un dépôts YUM
---------------------

Nous souhaitons faire un miroir du dépôt de CentOS 7.5.1804 OS 64 bits depuis le site distrib-coffee.ipsl.jussieu.fr

Le type

    YUM

L'URL racine

    http://distrib-coffee.ipsl.jussieu.fr/pub/linux/centos/7.5.1804/os/x86_64/.
    C'est sous ce répertoire que l'on trouve le dossier ``repodata``.

La distribution

    Le nom de la distribution, ici : centos.

La version

    La version est ici : 7.5.1804.

L'architecture

    L'architecture x86_64.

.. note::

    Pour cloner tous les dépôts nécessaires à un système CentOS 7.5.1804 il faudra donc créer un dépôt pour chaque dépôts 
    (os, updates, extras).

Créer un dépôt
--------------

Pour créer un dépôt allez dans ``Repositories`` puis dans la section ``List of repositories`` cliquez sur ``Add a repository``.

Synchroniser un dépôt
---------------------

Pour synchroniser un dépôt, une action de synchronisation doit être lancé. 
Cette action peut être lancé instantanément (tâche/task) ou être programmé (tâche programmée/scheduled task) pour se répéter à une heure donnée certain jour.

Depuis l'interface YARUS allez sur la page du dépôt que vous souhaitez synchroniser : ``Repositories`` puis dans la liste des dépôts cliquez 
sur le nom de celui à synchroniser. Dans la section ``Actions / Tasks / Scheduled tasks`` cliquez sur ``Sync`` sur la ligne ``Task`` pour lancer 
la tâche maintenant et sur la ligne ``Schedule a task`` pour programmer une synchronisation régulière.




