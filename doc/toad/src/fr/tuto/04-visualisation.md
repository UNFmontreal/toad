# Visualisation des images traitées par TOAD

L’équipe de TOAD recommande d’utiliser principalement deux logiciels pour visualiser les données :  

1. **`freeview`** (dépendance de `FreeSurfer`) pour l’ensemble des images anatomiques, de diffusion, les segmentations ou masques

2. **`fibernavigator`** pour visualiser les faisceaux

Ces deux logiciels sont librement disponibles sur Internet et ils sont également installés sur les serveurs de l’UNF (et donc accessible depuis une connexion ssh avec l’option `-Y`). 

***Si vous utilisez des images issues de fibernavigator vous devez ajouter cette référence à votre papier:*** *Chamberland M., Whittinstall K., Fortin D., Mathieu D., and Descoteaux M., "Real-time multi-peak tractography for instantaneous connectivity display." Frontiers in Neuroinformatics, 8 (59): 1-15, 2014.*

***Il est déterminant de vérifier vos images aux différentes étapes et non simplement les images qui serviront aux analyses. De même, et pour rappel, vous devriez toujours vérifier vos données avant de lancer une quelconque analyse ou prétraitement, y compris TOAD.*** 

Pour l’ensemble des visualisations, **vous devrez vous connecter sur un des serveurs de l’UNF** (Stark ou Magma) en connection ssh : `ssh -Y username@stark.criugm.qc.ca`. 
Les commandes présentées ci-dessous sont à exécuter depuis le répertoire de travail d’un participant donné de TOAD (par défaut le dossier `toad_data`, voir []()). 

<!-- FIXME add cross-ref -->


## 01-Preparation
Pour visualiser les données brutes :

```bash
# Données anatomiques
freeview 01-preparation/anat_*.nii.gz

# Données de diffusion
freeview 01-preparation/dwi_*.nii.gz

# B0s avec une phase d'encodage différente
freeview 01-preparation/b0_ap_*.nii.gz
freeview 01-preparation/b0_pa_*.nii.gz
```

La navigation dans les différents volumes s’effectue avec `frame` selon les différentes directions.
Si l’intensité des contrastes est trop faible (images non/peu visibles), il suffit de modifier l’option `Max` en bas à gauche (par exemple à 500).

Il faut rechercher des artefacts d’acquisition éventuels (trou, déformation, signaux aberrants) ou encore un mouvement trop important entre les volumes. 
Vous pouvez aussi vérifier les images B0 AP et PA en fonction de la position des déformation antérieure/postérieure.

<!-- FIXME cf interface, termes et description -->

## 02-Parcellation
La visualisation des données parcellées s’effectue avec les commandes suivantes:

```bash
# Masque du cerveau
freeview 02-parcellation/anat_*.nii.gz `ls 02-parcellation/brain_mask*.nii.gz`:opacity=0.25

# Parcellation
freeview 02-parcellation/anat_*.nii.gz -v 02-parcellation/aparc_aseg.nii.gz:colormap=lut:opacity=0.25
```

<!-- cf ajout commande en fonction fichiers + Ajouter les liens -->

Si vous rencontrez des problèmes prétraitement, nous vous recommandons de vérifier la documentation et la mailing list de <a href="https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI" target="_blank">Freesurfer</a> et en dernier recours de contacter les membres de TOAD sur la mailing list.

## 04-Denoising
Si vous avez débruité vos données il est extrêment important de valider la correction en visualisant vos données:

```bash
freeview `ls 00-backup/dwi_*.nii.gz`:grayscale=0,500 `ls 04-denoising/dwi_*_denoise.nii.gz`:grayscale=0,500
```

Changement à effectuer une fois l'interface ouverte:

`Frame` = minimum 2

**Vous devrez passer d'une image à l'autre** (dwi et denoised) en cochant l’image dans laquelle vous voulez naviguer. 

<!-- Changer les frames (autres directions) Attention car changer sur les deux images. Changement avec coche/décoche -->

## 05-Correction
Les corrections apportées aux images de diffusion sont visualisables avec les commandes:

```bash
# Pour des images qui ont été débruitées
freeview 04-denoising/dwi_*_denoise.nii.gz 05-correction/dwi_*_eddy_corrected.nii.gz

# Pour des images non débruitées
freeview 00-backup/dwi_*.nii.gz 05-correction/dwi_*_eddy_corrected.nii.gz
```

Les mêmes vérifications et options que celles proposées pour le débruitage (denoising, section précédente) sont à appliquées ici.

## 07-Registration
La coregistration des images anatomiques et de diffusion est visible avec la commande:

```bash
freeview 07-registration/anat_*_resample.nii.gz `ls 06-upsampling/b0_*_denoise_*upsample.nii.gz`:opacity=0.60
```

Comme précédement, vous pouvez manipuler l’opacité pour vérifier si les images sont bien recallées.

## 10-Tensorfsl - 11-Tensormrtrix - 12-TensorDipy

Vous pouvez visualiser si la reconstruction des tenseurs correspond bien à vos données DWI:

```bash
# Sum of Squares Errors map (sse)
freeview 10-tensorfsl/dwi_*_sse.nii.gz 
```

Vous avez ensuite plusieurs façon de visualiser les tenseurs:
```bash
# FSL
fslview 10-tensorfsl/*fa.nii.gz 10-tensorfsl/*v1.nii.gz
# i --> Display as Lines (RGB)

# Freeview
freeview 10-tensorfsl/*fa.nii.gz  `ls 10-tensorfsl/*v1.nii.gz`:render=line:inversion=z

# Fibernavigator
fibernavigator 12-tensordipy/*fa.nii.gz
# Option --> Color Maps -> Grey
# File --> Open 12-tensordipy/*tensor.nii.gz (pour voir les tenseurs)
# Display --> Maximas (pour voir les tensors en forme de batons)
# File --> Open 12-tensordipy/*tensor_rgb.nii.gz (pour voir la carte RGB)

# Les cartes RGB et/ou de tenseurs doivent avoir le corps calleux en rouge, le cortico spinal en violet/bleu et les faisceaux antérieur postérieur en vert
```

## 13-HardiMRtrix - 14-HardiDipy
La modélisation HARDI peut être visualisée avec la commande : 

```bash
fibernavigator 07-regitration/anat_*.nii.gz

# Option -> Color Maps -> Grey
# File -> Open 14-hardidipy/*.csd.nii.gz (très long à charger)
```

# 15-TractographyMRtrix - 17-TractQuerier - 18-TractFiltering

La visualisation des faisceaux peut s’effectuer grâce à la commande suivant:
``` bash
# Fibernavigator
fibernavigator 07-registration/anat_*.nii.gz
# File --> Open 15-tractographymrtrix/*.tck (ou trk)
# File --> Open 17-tractquerier/*.trk
# File --> Open 18-tractfiltering/raw/outlier_cleaned_tracts/*.trk
```

# Tutorials Fibernavigator
<a href="http://www.youtube.com/watch?feature=player_embedded&v=8X_eOB9zYU8
" target="_blank"><img src="http://img.youtube.com/vi/8X_eOB9zYU8/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>

# Tutorials Freesurfer
<a href="http://www.youtube.com/watch?feature=player_embedded&v=8Ict0Erh7_c
" target="_blank"><img src="http://img.youtube.com/vi/8Ict0Erh7_c/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>

# Autres logiciels pour visualiser vos données

<a href="http://www.mrtrix.org/" target="_blank">MRtrix</a>,  <a href="http://trackvis.org/docs/?subsect=instructions" target="_blank">TrackVis</a>
