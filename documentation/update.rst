Mise à jour
===========

Pour mettre à jour YARUS.

Télécharger les nouvelles sources de YARUS::

    $ git clone https://github.com/alexandreborgo/yarus

Se mettre dans l'environnement Python de YARUS::

    $ source /opt/yarus/env/bin/activate

Mettre à jour YARUS::

    $ cd yarus
    $ python -m pip install -I ./common ./webui ./engine ./tasksmanager

Redémarrer les services::

    $ systemctl restart httpd.service
    $ systemctl restart yarustaskmanager.service

Reconstruire la documentation::

    $ cd documentation
    $ make html