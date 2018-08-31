Règles d'associations
=====================

Les règles d'associations permettent de définir à quel canal sera associé un nouveau système qui s'enregistre (manuellement ou automatiquement).

Comment définir une règle
-------------------------

Un règle est définis à partir de deux informations d'un système :

* la distribution du système
* et sa version

Et associe à ces deux informations un canal.

Par exemple si une règles associe CentOS 7.5.1804 au canal CentOS 7.5, tout système qui s'enregistre avec ces informations sera automatiquement associé
au canal CentOS 7.5.

.. note::

    Si un système ne correspond à aucune règle il ne sera pas associé à un canal.


Ajouter une règle
-----------------

Pour ajouter une règle allez dans ``Systems auto-configuration`` puis cliquez sur ``Add a rule``