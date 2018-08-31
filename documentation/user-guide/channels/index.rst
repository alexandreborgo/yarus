Les canaux
===========

Un canal regroupe l'ensemble des dépôts que l'on souhaite associé à chaque système de même distribution et version.
Par exemple : les systèmes CentOS 7.5.1804 devront tous être associé au canal CentOS 7.5 qui devrai contenir tous 
les dépôts de cette distribution et version.

Informations requises
---------------------

Nom

    Le nom du canal

Description

    Une Description

La distribution

    La distribution qui est associé 

La version

    La version qui est associé


Créer un canal
--------------

Pour créer un canal allez dans ``Channels`` puis dans la section ``List of channels`` cliquez sur ``Add a channel``.


Ajouter des dépôts à un canal
-----------------------------

Sur la page d'un canal dans la section ``Repositories in the channel`` vous pouvez voir les dépôts qui sont associés au canal, pour en ajouter allez 
dans la section ``Add a repository to the channel``.


Synchroniser un canal
----------------------

La synchronisation d'un canal synchronisera tous les dépôts qui en font partie.

Pour synchroniser un canal, une action de synchronisation doit être lancé. 
Cette action peut être lancé instantanément (tâche/task) ou être programmé (tâche programmée/scheduled task) pour se répéter à une heure donnée certain jour.

Depuis l'interface YARUS allez sur la page du canal que vous souhaitez synchroniser : ``Channels`` puis dans la liste des canaux cliquez 
sur le nom de celui à synchroniser. Dans la section ``Actions / Tasks / Scheduled tasks`` cliquez sur ``Sync`` sur la ligne ``Task`` pour lancer 
la tâche maintenant et sur la ligne ``Schedule a task`` pour programmer une synchronisation régulière.





