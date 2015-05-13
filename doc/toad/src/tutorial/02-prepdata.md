# Préparation des données
---

## Type de données et format des fichiers

### Type de données 

Les analyses de diffusion nécessitent la présence d’au moins trois types de données par participant :

1. **données anatomiques** (T1, type MPRAGE) : création des masques anatomiques, coregistration
2. **données de diffusion** (DWI) : faisceaux de matière blanche (extraction des fibres)
3. **données d’encodage :** spécification relatives aux données de diffusion

D’autres données peuvent servir à TOAD pour le traitement des données :

- **Direction des gradients** (Eddy Correction) : fichiers des gradients antérieur-postérieur ou postérieur-antérieur
- **inhomogénéité du champ** (fieldmap) : fichiers donnant le fichier de magnitude et de phase (limité aux cartes de Siemens)

### Format des fichiers

Pour des raisons de simplicité, TOAD accepte seulement quelques formats :

- neuroimagerie : **format nifti compressé** (.nii.gz)
- encodage :  format regroupé **MRTRIX (.b)** ou séparé en valeurs et vecteurs **(.vals et .vecs)**.


## Préparation des données 

### Conversion des fichiers

TOAD propose un logiciel de conversion des données dénommé `unf2toad`. 
Non seulement `unf2toad` va pouvoir convertir les données brutes d’un participant (en format dicom ou .tar.gz issu de l’UNF) ou d’un groupe de participants, mais le logiciel va aussi appliqué une nomemclature commune aux différents types de fichier.
Cette [nomenclature](#nomenclature) peut être personnalisée, `unf2toad` va alors créer le fichier de configuration nécessaire au lancement de TOAD.
Cette nomencalture commune est nécessaire pour que TOAD puisse identifier correctement les fichiers à utiliser. 

### Lancer la conversion

Pour lancer la conversion des données, il suffit de suivre la procédure suivante :

1. se connecter à un des serveurs de l’UNF (stark ou magma)

    ```# ssh -Y usersname@stark.criugm.qc.ca
    ```

2. naviguer jusqu’au dossier contenant les données à convertir (dossier contenant le ou les sessions UNF `*.tar.gz` ou les dossiers des sujets) 
    
    ```# cd /grpname/username/projectname
    ```

3. lancer la commander `unf2toad .` où le point indique d’utiliser le dossier courrant pour la conversion. Vous pouvez remplacer ce point par le chemin vers le ou les dossiers à convertir
    
    ```# unf2toad .
    ```

4. répondre aux différentes questions posées par le logiciel.


### Données déjà converties

Si vous disposez de données déjà converties au format nifti ainsi que des fichiers d’encodage, vous pouvez utiliser TOAD sans passer la conversion au préalable.
Nous vous recommandons de regrouper les données de la façon suivante :

- un dossier parent contenant tous les dossiers participants
- chaque dossier participant contenant tous les fichiers de neuroimagerie (\*.nii, \*.b) 

```shell
    PROJET  
    |- Subject1  
        |- anat_subject1_.nii.gz
        |- dwi_subject1_.nii.gz
        |- b0_subject1_.b  
    |- Subject2  
    |- Subject3  
    |- ...  
```
    
***Attention :*** *dans ce cas de figure, il est de votre responsabilité de vous assurer les données ont été correctement converties et que le fichier d’encodage respecte bien les normes habituelles (strides...).
Afin d’éviter tout problème, si vous disposez encore des données brutes, nous recommandons fortement de reconvertir les données avec le logiciel `unf2toad`.*


### <a name="nomenclature"></a> Nomenclature des fichiers

TOAD doit identifier quels fichiers correspondent à quels types d’images. 
Pour ce faire, TOAD se base sur des préfixes des noms des fichiers qui doivent être communs pour chaque type de fichiers.
Ainsi, toutes les images anatomiques devront commencer par un même préfixe, par défaut TOAD cherchera des fichiers commençant par `anat`.
Pour les images de diffusions, TOAD cherchera des fichiers commençant par `dwi` et pour l’encodage à `b0`. 
Lorsque les données antérieur/postérieur ou postérieur/antérieur sont disponibles, TOAD cherchera comme préfixe `b0_ap` et `b0_pa`.

Ainsi, les fichiers pour un participant dont le code est PSY01 seront :
```shell
PSY01
|- anat_PSY01.nii.gz
|- dwi_PSY01.nii.gz
|- b0_ap_PSY01.nii.gz
|- b0_pa_PSY01.nii.gz
```

Vous êtes libres cependant d’utiliser n’importe quelle nomenclature du moment qu’elle soit indiquée dans le fichier de configuration `config.cfg`. 
Cette nomenclature devra être constante à travers les sujets à moins de spécifier un nouveau fichier de configuration au sein du dossier du participant en question.

<br/>
**Tableau 1 :** synthèse des préfixes par défaut utilisé par TOAD

| Type de fichier                       | Préfixe par défaut    |
|---------------------------------------|-----------------------|
| **Anatomique** (T1)                   | anat_                 |
| **Diffusion** (DWI)                   | dwi_                  |
| **Carte de B0** (antérieur-postérieur)  | b0_ap_                |
| **Carte de B0** (postérieur-antérieur)  | b0_pa_                |
