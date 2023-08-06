=======
Contenu
=======

Liste non-exhaustive :

BatchDirCovers.py
    Scanne récursivement un répertoire à la recherche d'icone de répertoire. Ce script 
    sert à générer ou régénérer les icones de répertoires d'albums musicaux.
DocExport.py
    Un module le nécessaire pour exporter du contenu sous forme de documents 
    Html/Xml/etc.. Cette classe est utilisé dans différents projets Django tel que 
    'Shoop' pour exporter son Wiki ou bien 'Dad' pour exporter des rapports..
ToExcel.py
    Exportation de données vers un nouveau fichier Excel.
TreeMaker.py
    Module qui calcule une arborescence à partir d'une liste "plate" d'éléments liés 
    entre eux par un attribut de "parenté".
logger
    Un module qui gère les messages de debug, info, warning, error dans la  sortie de 
    terminal et fichier de logs. Elle permet d'avoir une interface unifiée pour gérer 
    tout ces messages, la verbosité, les sorties de scripts en cas d'erreur, etc.. Une 
    fois instanciée, il suffit de passer son objet à tout les éléments qui en ont besoin.
chan
    Un module pour faire du scan et téléchargement d'images sur les Chans.
cli
    Utilitaires de facilités pour créer des outils en ligne de commande.
django.attachments
    Une brique pour gérer les fichiers joignables à des documents.
django.gallery
    Une brique pour gérer une galerie d'albums d'images avec redimensionnement 
    automatique.
django.mailings
    Système de gestion d'envois de mails avec des templates modifiables dans 
    l'administration et un historique d'envois.
django.news
    Une brique pour un simple espace d'actualités catégorisés.
django.protoforms
    Système de gestion de formulaires avec plusieurs options de mise en forme sans avoir 
    à rédiger un template à chaque fois et avec des types de champs supplémentaires etc..
django.pywiki2xhtml
    Une brique sans modèles de données, unique le nécessaire (vue, templates, tags, 
    etc..) pour intégrer facilement l'utilisation de la syntaxe wiki2xhtml dans un 
    projet.
django.queues
    Système simple pour ajouter des tâches programmées dans des applications Django.
django.tags
    Des templetags ou filter utiles
gantt
    Module pour générer des diagrammes de gantt. Directement en Python via 
    l'intermédiaire de ``PIL``.

==========
Pré-requis
==========

* Python >= 2.5;
* Django >= 1.3 (facultatif) (Pour les modules ``django.*`` et ``DjangoCLI``);
* BeautifulSoup >= 3.0 (facultatif) (Pour ``chan``);
* xlwt >= 0.7.2 (facultatif) (Pour ``ToExcel``);
* Python Imaging Library (PIL) >= 1.1.6 (facultatif) (Pour ``gantt``);
* PyWiki2Xhtml pour certains modules ``django.*``;

À notez qu'en général les modules dans Sveetchies sont interdépendants.
