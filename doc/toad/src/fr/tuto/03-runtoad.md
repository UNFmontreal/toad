# TOAD

##  Lancement de TOAD

Une fois la conversion des données d’imagerie effectuée, il suffit de lancer la commande `toad` depuis le dossier contenant les fichiers convertis :

~~~bash
# Déplacement dans le dossier des données converties
cd toad_data

# Lancement de TOAD
toad .
~~~

Le traitement complet d’un participant prend environ 2 jours. 
Plusieurs participants peuvent être traités en parallèle sur les serveurs selon la charge qu’ils subissent à ce moment-là. 

## Vérifications

### Traitement en cours

Sur les serveurs de l’UNF, il est possible de savoir combien de sujets sont actuellement traités avec la commande `qstat -f`.

Si vos données sont toujours en cours de traitement, vous devriez voir apparaître votre nom d’utilisateur associé au nom du sujet traité et au logiciel en cours d’utilisation (comme FreeSurfer). 

En cours de traitement, vous pouvez visualiser le contrôle qualité des différentes étapes au fur et à mesure de leur complétion avec la commande suivante : `firefox 00-qa/index.html` (voir ci-dessous). 

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
|03-atlas               | Création et application des atlas                     |
|04-denoising           | Débruitage des images                                 |
|05-correction          | Correction mouvement, inhomgénéité du champs, etc.    |
|05-preprocessing       |                                                       |
|06-upsampling          | Mise à l’échelle des images                           |
|07-registration        | Registration T1/DWI                                   |
|08-atlasregistration   |                                                       |
|09-masking             | Création des masques                                  |
|08-snr                 | Calcul du rapport signal sur bruit                    |
|10-tensorfsl           | Reconstruction des tenseurs (FSL)                     |
|11-tensormrtrix        | Reconstruction des tenseurs (MRTRIX)                  |
|12-tensordipy          | Reconstruction des tenseurs (Dipy)                    |
|13-hardimrtrix         | Reconstruction HARDI (MRTRIX)                         |
|14-hardidipy           | Reconstruction HARDI (Dipy)                           |
|15-tractographymrtrix  | Reconstruction des faisceaux (MRTRIX)                 |
|16-tractographydipy    | Reconstruction des faisceaux (Dipy)                   |
|17-snr                 | Calcul du ratio signal sur bruit                      |
|18-outputs             | Regroupe tous les fichiers exploitables (images débruités, resamplées, tensors, tracto, ...) |                                                  
|99-logs                | Fichiers logs et erreurs                              |

*Note :* Il est possible que cet arbre change avec les versions de TOAD. 
De même, le choix de certains paramètres au lancement de TOAD ou l’absence de certains type de fichiers (comme les B0 AP/PA) font que certaines tâches ne seront pas exécutées. 

Ainsi, une première vérification du bon déroulement de TOAD consiste à vérifier que ces dossiers ont bien été créés pour chaque participant.
L’absence d’une série de dossier indique que le pipeline a probablement rencontré un problème et a dû s’arrêter pour le participant en question.

Dans ce cas, il est utile d’aller regarder le dernier log produit par TOAD. 
Ce fichier `*.log` se trouvera dans le dernier répertoire créé par TOAD ou alors dans le dossier `99-logs`.
Ce dossier de logs renferme également un fichier regroupant les erreurs rencontrées par TOAD, et possède un nom du type `numéro_sujet.e1111` où 1111 correspond au numéro de travail de la tâche dans le système.

Les résultats peuvent être rapidement évalués grâce aux QA.

### Quality Assessment

TOAD offre une interface simple et pourtant complète pour explorer la qualité des données et des résultats obtenus.

Pour lancer le QA, il suffit d’ouvrir la page internet du QA grâce à la commande : `firefox 00-qa/index.html`.
L’ouverture de la fenêtre prendra un peu de temps afin de charger les différentes images associées au QA.

*Attention:* pour que la commande fonctionne, il faut avoir lancé votre session SSH avec l’option `-Y` pour permettre l’envoi de données graphiques (donc `ssh -Y username@stark.criugm.qc.ca`). 

La page internet s’ouvrira sur une page d’accueil qui propose aussi des liens vers chacune des tâches.
Vous trouverez alors les principales métriques et images qui permettent d’évaluer la qualité de vos données et le bon fonctionnement de TOAD.

Par exemple, vous pourrez observer l’effet de la correction grâce aux gifs avant/après, ou encore voir les ratios signal sur bruit, etc.

En cas de problème, vous trouverez plus d’informations dans le dossier log, consultable dans chacun des dossiers traités par TOAD :

~~~bash
# Remplacer 'toad_data' par le nom du dossier utilisé lors de la conversion 
cd toad_data/subject_name/99-logs

# Lister les logs disponibles
ls

# Consultation d’un fichier log, ici results.log
vi results.log
~~~

## Usage avancé et en cas de problème

## Options de TOAD

Il est possible de connaître les différentes options de TOAD en tapant simplement `toad` dans la console. 
Vous verrez alors apparaître la liste des options à ajouter à TOAD pour lancer seulement certaines tâches, pour ajouter certains paramètres ou éviter certaines étapes.

Voici deux commandes qui pourraient particulièrement vous servir.

## Lancer TOAD pour un seul sujet

`toad foldername` où 'foldername' désigne le nom d’un dossier de participant.

## Réinitialiser vos données

TOAD sauvegarde vos données brutes (converties après `dcm2toad` par exemple) et peut revenir à cet état antérieur avec la commande : `toad -r .`. 

Vous pouvez aussi réinitialiser les données que d’un participant avec la commande : `toad -r foldername`
 où 'foldername' désigne le nom d’un dossier de participant.

## Exemple de problème

Il est possible que vous rencontriez quelques problèmes durant le traitement des données. 
Par exemple, TOAD pourrait vous informer que l’algorithme utilisé par défaut (NLMEANS) n’est pas compatible avec les données que vous avez. 
Dans ce cas, il faudra annuler le traitement des données qui sera lancé malgré tout.

Pour ce faire, placer vous dans le terminal (session SSH) dans votre dossier de travail :

1. Vérifier si vos participants sont en cours de traitement avec la commande : `qstat -f`
2. Arrêter le travail en cours par particiapnt avec la commande : `qdel #id` où "#id" correspond au numéro de processus affiché par qstat. 
3. Réinitialiser les données avant le traitement de TOAD avec la commande : `toad -r .` TOAD affichera un avertissement comme quoi les processus sont vérouiller. Il faudra appuyer sur `r` et valider pour que TOAD enlève ce verrou pour réinitiliser les données.
4. Apporter les modifications nécessaire à vos données ou au fichier de configuration (par exemple ajouter un fichier "config.cfg" dans le dossier de travail avec l'option `algorithm=lpca` sous la section `[denoising]`)
5. Relancer TOAD avec la commande : `toad .`

**Pensez à consulter la documentation** relative à chacune des tâches de TOAD pour plus d’informations.

