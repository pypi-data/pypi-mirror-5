Présentation
============

Kiwi est un module Django dont le but est de gérer des pages Wiki. Il a pour 
particularité de permettre de gérer les pages dans une arborescence par un 
système de ''parenté''. Par défaut il utilise le parser **PyWiki2Xhtml**, mais 
il est fait pour accepter n'importe quel autre parser tel que ceux des 
''templates tags'' fournis par Django pour ``markup``, ``textile`` et ``ReST``.

Il n'a pas pour Kiwi est un module Django dans le but est de gérer des pages 
Wiki. Il a pour particularité de permettre de gérer les pages dans une 
arborescence par un système de ''parenté''. Par défaut il utilise le parser 
**PyWiki2Xhtml**, mais il est fait pour accepter n'importe quel autre parser 
tel que ceux des ''templates tags'' fournis par Django pour ``markup``, 
``textile`` et ``ReST``.

Il n'a pas pour but d'être un wiki collaboratif ''ouvert'', c'est à dire que 
les rédacteurs doivent avoir un compte sur l'administration ''automatique'' 
fournis dans Django et qu'il n'y a pas un système de permissions internes à 
Kiwi limitant l'édition de pages pour des utilisateurs particulier.

Kiwi est donc utilisable de base comme un site de wiki ''autonome'', il peut 
aussi servir de module wiki dans un autre projet, pour un site de 
documentation, ou pour les pages de certains sites vitrines. Dans le cas d'un 
site de documentation, un outil d'exportation est aussi inclus pour exporter 
les pages visibles du wiki comme fichiers html lisibles en dehors du site.

Installation
============

Pré-requis
----------

* **Python 2.5** et sa librairie devel souvent nommée lib-pythonX.X-dev.
* **Django** 1.3.x Django Installation guide|http://docs.djangoproject.com/en/dev/intro/install/#intro-install et son nécessaire.
* **PyWiki2xhtml** PyWiki2xhtml|http://svn.logicielslibres.info/bordel/sveetch/PyWiki2xhtml/ si vous comptez l'utiliser comme parser de syntaxe wiki pour vos textes. Sinon installez votre parser préféré ainsi que son ''template tag'' (s'il n'est pas déja inclus dans Django).
* **Sveetchies** Sveetchies|http://svn.logicielslibres.info/bordel/sveetch/Sveetchies/ si vous comptez utiliser l'outil d'exportation fourni dans Kiwi.
* Un compte et une base de donnée sur un serveur de type PostgreSQL, MySql ou Sqlite au choix ainsi que son binding Python.

Module Kiwi
-----------

Vous devrez ensuite indiquer le répertoire de ``$KIWI_PROJECT/kiwi`` dans 
votre ``PYTHONPATH``. Sous Ubuntu, il vous faut ajouter (ou l'éditer si elle 
existe déja) la ligne suivante à votre fichier ``$HOME/.profile`` :

    PYTHONPATH=$PYTHONPATH:$HOME/mon/chemin/vers/kiwi

Relancez ensuite votre session ou rechargez votre configuration shell pour que 
cette modification soit effective. De cette facon Kiwi sera toujours disponible 
en tant que module Python.

Autonome
--------

Le projet Kiwi contient deux répertoires qui sont ``kiwi`` et ``examplesite``. 
Le premier est le module Python à installer, le second est un exemple tout 
prêt pour utiliser Kiwi en tant que site autonome, c'est à dire sans l'importer 
dans un de vos projet Django.

Dès lors que vous avez suivi toute les étapes sans problèmes, vous pourrez 
l'utiliser en faisant les commandes suivantes depuis le répertoire 
``examplesite`` :

(Reportez vous à la documentation de Django pour plus de détails)

Installez la BDD
................
    
    python manage.py syncdb

Lancez le serveur
.................
    
    python manage.py runserver 0.0.0.0:8001

Utilisez
........

Le serveur est accessible sur le nom ou l'adresse IP de votre machine : 
    
    http://votremachine:8001/
    
Utiliser l'interface d'admin pour rentrer du contenu, à l'adresse :
    
    http://votremachine:8001/admin/

Pensez à renseigner dans le modèle **Site** la bonne url que vous souhaitez 
utiliser pour accéder à votre serveur.

Contenu de la documentation
...........................

``Attention``, les données comportent déja un superutilisateur, vous devez donc 
avoir répondu ``no`` à la question de la commande ``python manage.py syncdb`` 
que vous avez pu faire dans l'étape précédente. Si ce n'est pas le cas, 
remettez votre base de donnés à zéro et relancez la commande en répondant ``no`` 
cette fois ci.

Pour une démonstration complète avec du contenu, vous pouvez charger les 
données de la documentation qui sont fournis dans Kiwi. Il vous suffit de 
lancer la commande suivante depuis le répertoire ``examplesite`` :

    python manage.py loaddata kiwi_doc.json

Relancez le serveur et voila. Attention, le site configuré utilise le port 
8001, si vous en utilisez un autre, pensez à le mettre à jour dans le modèle 
**Site**.

Il y aura deux utilisateurs déja inscrits :

* ``root``, mot de passe ``root``, c'est un superutilisateur pour pouvoir 
administrer complètement le site.
* ``demo``, mot de passe ``demo``, c'est un utilisateur pour la rédaction, qui 
ne possède que les droits pour ajouter, éditer et supprimer des ``Wikipage``, 
ainsi que des ``Version`` (nécessaire pour supprimer des Wikipage qui y sont liés).

Dans un projet Django existant
------------------------------

Comme Kiwi est installé en tant que module Python dans ``PYTHONPATH``, il est 
tout de suite intégrable dans votre projet, la première chose pour l'activer 
est donc de le rajouter dans vos settings comme application installée, dans 
``INSTALLED_APPS`` ajoutez donc juste une entrée ''kiwi''.

Ensuite, charge à vous d'intégrer au moins ses urls. Vous pouvez aussi faire 
vos propres templates en les mettant dans le répertoire ``templates/kiwi/`` de 
votre projet, ils écraseront ceux déja fournis dans Kiwi.
