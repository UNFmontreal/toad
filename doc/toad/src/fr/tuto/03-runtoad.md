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


## Vérifications

### Traitement en cours

Sur les serveurs de l’UNF, il est possible de savoir combien de sujets sont actuellement traités avec la commande `qstat -f`.

Si vos données sont toujours en cours de traitement, vous devriez voir apparaître votre nom d’utilisateur associé au nom du sujet traité et au logiciel en cours d’utilisation (comme FreeSurfer). 

En cours de traitement, vous pouvez visualiser le contrôle qualité des différentes étpaes au fur et à mesure de leur complétion en ouvrant le fichier `00-qa/index.html`. Voir aussi la section [00-QA](tasks/#00-qa).

### Post traitement

Une fois le travail terminé, vous trouverez un ensemble de nouveaux dossiers dans chacun des répertoires sujets.
*Pour rappel*, ce dossier est par défaut inclus dans le dossier initial de votre projet sous le nom de `toad_data` ou de celui que vous lui avez spécifié lors de la conversion des données par `dcm2toad`.
 
Ces nouveaux dossiers contiennent l’ensemble des données, masques, et images produits par TOAD lors du traitement des données de diffusion.
L’ensemble des dossiers pour chaque sujet devrait ressembler à peu près au tableau ci-dessous :

|**Nom du dossier**     | **Type de données**                                   |
|-----------------------|-------------------------------------------------------|
|00-backup              | Données originales (Nifti)                            |
|00-qa                  | Quality Assessment - pages HTML de synthèse           |
|01-preparation         | Réorientation des images si nécessaire                |
|02-parcellation        | Parseg et Brodmann, gauche/droite (Freesurfer)        |
|03-denoising           | Débruitage des images                                 |
|04-correction          | Correction mouvement, inhomgénéité du champs, etc.    |
|05-preprocessing       |                                                       |
|06-registration        | Registration T1/DWI                                   |
|07-masking             | Création des masques                                  |
|08-snr                 | Calcul du rapport signal sur bruit                    |
|09-tensorfsl           | Reconstruction des tenseurs (FSL)                     |
|10-tensormrtrix        | Reconstruction des tenseurs (MRTRIX)                  |
|11-tensordipy          | Reconstruction des tenseurs (Dipy)                    |
|12-hardimrtrix         | Reconstruction HARDI (MRTRIX)                         |
|13-hardidipy           | Reconstruction HARDI (Dipy)                           |
|14-tractographymrtrix  | Reconstruction des faisceaux (MRTRIX)                 |
|15-tractographydipy    | Reconstruction des faisceaux (Dipy)                   |
|16-outputs             |                                                       |
|99-logs                | Fichiers logs et erreurs                              |

*Note :* Il est possible que cet arbre change avec les versions de TOAD. 
De même, le choix de certains paramètres au lancement de TOAD ou l’absence de certains type de fichiers (comme les B0 AP/PA) font que certaines tâches ne seront pas lancées. 

Ainsi, une première vérification du bon déroulement de TOAD consiste à vérifier que ces dossiers ont bien été créés pour chaque participant.
L’absence d’une série de dossier indique que le pipeline a probablement rencontré un problème et à dû s’arrêter pour le participant en question.

Dans ce cas, il est utile d’aller regarder le dernier log produit par TOAD. 
Ce fichier `*.log` se trouvera dans le dernier répertoire créé par TOAD ou alors dans le dossier `99-logs`.
Ce dossier renferme également un fichier regroupant les erreurs rencontrées par TOAD, et possède un nom du type `numéro_sujet.e1111` où 1111 correspond au numéro de travail de la tâche dans le système.


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

