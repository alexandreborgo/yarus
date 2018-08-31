Les tâches
==========

Les tâches peuvent être lancées depuis la page de chaque objet (dépôt, canal, système, groupe)

.. note::

    Plusieurs tâches associées à un objet ne peuvent pas s'exécuter en même temps. Elles seront exécutées les unes après les autres dans leur ordre 
    de création.

Sync
----

La tâche de synchronisation peut s'exécuter sur un dépôt ou un canal. Elle met à jour le dépôt local.

Check
-----

Cette tâche vérifie que YARUS peut se connecté à un système ou groupe de systèmes via Ansible (SSH).

Configure
---------

Cette tâche configure les dépôts sur un système ou groupe de systèmes. Pour YUM ajouter un fichier ``yarus.repo`` dans ``/etc/yum.repos.d`` 
et pour APT ajoute le fichier ``source.list`` dans le dossier ``/etc/apt``.   

List upgradable packages
------------------------

Récupère la liste des paquets qui peuvent être mis à jour sur un système ou un groupe.

Update approved packages
------------------------

Met à jour les paquets qui ont été approuvé pour un système ou un groupe.

Update all packages
-------------------

Met à jour tous les paquets pour un système ou un groupe.