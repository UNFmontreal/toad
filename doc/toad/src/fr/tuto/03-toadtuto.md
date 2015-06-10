# TOAD

##  Lancement de TOAD

Une fois la conversion des données d’imagerie effectuée, il suffit de lancer la commande `toad` depuis le dossier contenant les fichiers convertis :

~~~bash
# Déplacement dans le dossier des données converties
cd toad_data

# Lancement de TOAD
toad *
~~~

Le traitement complet d’un participant prend environ 2 jours. 
Plusieurs participants peuvent être traités en parallèle sur les serveurs selon la charge qu’ils subissent à ce moment-là. 


## Vérification

Sur les serveurs de l’UNF, il est possible de savoir combien de sujets sont actuellement traités avec la commande `qstat`.

Une fois le travail terminé, vous trouverez un ensemble de nouveaux dossiers dans chacun des répertoires sujets. 
Ces dossiers contiennent l’ensemble des données, masques, et images produits par TOAD pour le traitement des données de diffusions.
Les résultats peuvent être rapidement évalués grâce aux QA...

<!-- FIXME QA -->
*Section à développer*

En cas de problème, vous trouverez plus d’informations dans le dossier log, consultable dans chacun des dossiers traités par TOAD :

~~~bash
# Remplacer 'toad_data' par le nom du dossier utilisé lors de la conversion 
cd toad_data/subject_name/99-logs

# Lister les logs disponibles
ls

# Consultation d’un fichier log, ici results.log
vi results.log
~~~

