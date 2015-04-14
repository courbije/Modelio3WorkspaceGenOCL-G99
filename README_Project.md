
Projet IDM M2PGI G279 : SQLSCRIBE
===========================

XML -> Modelio

Le script se nomme SQLScribe2Modelio.py.
Il réalise la transformation complète d'un fichier XML provenant de SQLscribe en un diagramme de class sur modelio.
Le script pour fonctionné a besoin des pré-requis suivant : 
- Un projet doit être créer avec un package nommé SQLscribe (note : le scripte supprime l'intégrallité du contenue du package)
- 4 Stéréotypes doivent être créer : PK (Attribute), FK (Attribute), FKC (Dependency) et Table (Class)
- Le fichier XML doit se trouvé dans : ./macros/xml/library.xml
Si les pré-requis ne sont pas respecter le script ne fonctionne pas. Il n'effectue aucune vérification sur les pré-requis aucun message d'erreur n'est afficher

MODELIO -> SQL

Le script doit-être réalisé