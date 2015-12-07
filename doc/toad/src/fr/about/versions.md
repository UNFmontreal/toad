# Versions de TOAD

| Version                  | Date de sortie  | Nom | Commentaires                    |
| :----------------------- | :-------------: | :---: | :------------------------------: |
| [v01.1](versions.md###v01) | 2015-12-07   | **Anaxyrus**  | Nouvelles tâches (Atlas)  + dcm2toad option           |
| [v01](versions.md###v01) | 2015-08-24     | **Adenomus**  | 1ère version stable             |


## Journal des modifications

### v01.1

- Ajout de 2 nouvelles tâches:
  - Atlas (Création d'atlas)
  - Atlas Registration (Registration d'atlas)

- Ajout d'une option pour l'outil `dcm2toad` permettant d'utiliser un fichier texte pour définir le nom du dossier de sortie.
- Correctifs mineurs

### v01

- Structure finalisée du pipeline
- Première version de la documentation (tutoriel)
- Création de l’outil `dcm2toad` pour convertir les données brutes d’un scanner IRM Siemens Tim Trio 3T au format Nifti optimisé pour TOAD
