# Préparation des données
---

## Type de données et format des fichiers

### Type de données 

Les analyses de diffusion nécessitent la présence d’au moins trois types de données par participant :

1. **données anatomiques** (T1, type MPRAGE) : création des masques anatomiques
2. **données de diffusion** (DTI) 
3. **données d’encodage :** spécification relatives aux données de diffusion

D’autres données peuvent servir à TOAD pour le traitement des données :

- **inhomogénéité du champ :** fichiers antérieur-postérieur et postérieur-antérieur
- **...**

### Format des fichiers

Pour des raisons de simplicité, TOAD accepte seulement quelques formats :

- neuroimagerie : **format nifti** (.nii) 
- encodage :  format **MRTRIX (.b)** ou séparé **(.val et .vec)**.

TOAD a besoin que les données soient organisées d’une certaine manière afin de d’extraire les différents types d’images (anatomitiques, diffusions, etc.) pour les analyses.
De même, s‘il y a plusieurs participants à analyser, il faut également respecter une certaine organisation tel que présenté ci-dessous.


## Organisation des dossiers

TOAD s’appuie sur une nomemclature régulière pour trouver les fichiers à utiliser dans les analyses.
Pour ce faire, vous devez regrouper toutes les données dans un seul dossier (i.e. le projet) et ensuite chacune des images des participants dans un dossier différent. 

    - PROJET
    |- SUJ1
        |- anat.nii
        |- dti.nii
        |- enco.b
    |- SUJ2
    |- SUJ3
    |- ...
    
    
## Nomemclature des fichiers

TOAD doit identifier quels fichiers correspondent à quels types d’images. 
Pour ce faire, TOAD se base sur des racines des noms des fichiers qui doivent être communes pour chaque type de fichiers.
Ainsi, toutes les images anatomiques devront commencer par une même racine comme "MPRAGE","ANAT", "T1", etc.
De même, toutes les images de diffusions devront commencer par une même racine comme "DTI",  toutes les fichers d’encodage comme "ENCO", etc.

Par défaut, TOAD considère les noms suivants :

- Anatomique :
- Diffusion :
- Encodage :

Cependant, vous pouvez facilement préciser à TOAD quels nomenclatures suivrent en créant/modifant le fichier de configuration.
