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

Sur les serveurs de l’UNF, il est possible de savoir combien de sujets sont actuellement traités avec la commande `qstat`.

Si vos données sont toujours en cours de traitement, vous devriez voir apparaître votre nom d’utilisateur associé au nom du sujet traité et au logiciel en cours d’utilisation (comme FreeSurfer). 

### Post traitement

Une fois le travail terminé, vous trouverez un ensemble de nouveaux dossiers dans chacun des répertoires sujets.
*Pour rappel*, ce dossier est par défaut inclus dans le dossier initial de votre projet sous le nom de `toad_data` ou de celui que vous lui avez donné lors de la conversion des données par `unf2toad`.
 
Ces dossiers contiennent l’ensemble des données, masques, et images produits par TOAD pour le traitement des données de diffusions.
L’ensemble des dossiers pour chaque sujet devrait ressembler à peu près au tableau ci-dessous :

|**Nom du dossier** | **Type de données**                                   |
|-------------------|-------------------------------------------------------|
|00-backup          | Données originales (Nifti)                            |
|00-qa              | Quality Assessment - pages HTML de synthèse           |
|01-preparation     | Réorientation des images si nécessaire                |
|02-parcellation    | Parseg et Brodmann, gauche/droite (Freesurfer)        |
|03-eddy            | Correction mouvement, inhomgénéité du champs, etc.    |
|04-denoising       | Débruitage des images                                 |
|05-preprocessing   |                                                       |
|06-registration    | Registration T1/DWI                                   |
|07-masking         | Création des masques                                  |
|08-snr             | Calcul du rapport signal sur bruit                    |
|09-tensorfsl       | Calcul des tenseurs DTI (FSL)                         |
|10-tensormrtrix    | Calcul des tenseurs DTI (MRTRIX)                      |
|11-tensordipy      | Calcul des tenseurs DTI (DiPY)                        |
|12-hardimrtrix     | Calcul du modèle HARDI (MRTRIX)                       |
|13-hardidipy       | Calcul do modèle HARDI (DiPY)                         |
|16-results         |                                                       |
|99-logs            | Fichiers logs et erreurs                              |
|-------------------|-------------------------------------------------------|      

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

