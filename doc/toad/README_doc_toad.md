% DOCUMENTATION DE TOAD
% GT Vallet  
%

**Création:** 2014/11/25  
**Version:** v0.1  


Ce readme est destiné aux personnes qui souhaitent contribuer à la documentation du projet toad.
Vous trouverez ici les principales informations sur l’organisation de la documentation, la manière de contribuer, les étapes pour générer la documentation finale.

Pour toute question relative à la documentation, merci de contacter [Guillaume Vallet](mailto:gtvallet@gmail.com) ou les responsables des différentes sous-sections tel que présenté ci-dessous.


## Organisation de la documentation

La documentation de toad se situe dans le répertoire `doc` du projet toad.
Dans ce répertoire, vous trouverez le présent document, ainsi que le guide d’utilisation de subversion et finalement les dossiers des sous-projets de toad:

- **toad**: documentation pour toad lui-même 
- **toad-info**: documentation pour l’outil de configuration de toad *[à venir]*
- **convert_unf-info**: documentation pour l’outil de conversion DICOM-NIFTI de l‘UNF *[à venir]*

Dans chacun des sous-projets, vous trouverez un fichier `yaml` pour la configuration du site de documentation du sous projet ainsi qu’un dossier `html`, qui contiendra la version statique de la documentation, et un dossier `src` pour les sources markdown utilisées dans la documentation.

Pour résumer:

    toad
    |- doc
       |- convert_unf-info
          |- A venir 
       |- toad
          |- html
          |- src
          |- mkdocs.yml
       |- toad-info  
          |- A venir
       |- README_doc_toad.md
       |- subversion.rtf


## Écrire de la documentation

### Markdown

L’écriture de la documentation repose sur le format `markdown` qui permet d’écrire simplement du texte qui sera converti en html, PDF, etc. [(voir pandoc)][pandoc].
Markdown peut s’appendre en quelques minutes, car il a été créé pour être simple, lisible et portable. 
Vous trouverez un simple tutoriel en anglais [ici][tuto] et une documentation un peu plus avancée en français [ici][mkinfo].


### Tutoriel et QA

Ces deux sections sont principalement sous la responsabilité de [Guillaume Vallet (tuto)](mailto:gtvallet@gmail.com) et [Christophe Bedetti (QA)](mailto:christophe.bedetti@gmail.com). 
Merci de les contacter avant de modifier ces sections.

La documentation de ces sections se situe dans les dossiers `toad/doc/toad/src/tuto` et `toad/doc/toad/src/qa`. 


### Tâches

Les deux responsables des tâches sont [Mathieu Desrosier](mailto:mathieu.desrosiers@criugm.qc.ca) et [Arnaud Boré](mailto:arnaud.bore@gmail.com). 
Merci de communiquer avec eux pour les modifications à apporter à cette section.

La documentation de cette section respecte un template commun afin d’harmoniser le contenu et ainsi faciliter la lecture. 
Vous trouverez les templates dans le dossier `toad/doc/toad/src/tasks/` où chacune des tâches possède son propre fichier `xx-xxxx.md` avec xx pour le numéro de la tâche et xxxx pour son nom. 

**Afin de d’écrire cette documentation, merci de respecter les règles suivantes :**

- Compléter uniquement les sections indiquées entre crochets `[text à changer]`
- Indiquer les liens selon cette convention : appel dans le texte `(texte affiché)[1]` et références regroupées à la toute fin du document avec `[1]: url`. Le texte [1] sera remplacé par 'url'. Changer [1] par un numéro unique par référence ou par un identifiant simple.
- Si vous voulez utiliser des figures, merci de placer la source dans le dossier `toad/doc/toad/figs`, vous pourrez l’appeler dans le texte avec la commande `![texte alternatif](../figs/figname.jpg)`.
- L’utilisation de figure nécessite la citation de sa source de provenance (vérifier les droits d’utilisation !).


## Compiler la documentation statique

### Mkdocs

La gestion de la documentation s’appuie sur le module python [mkdocs][mkdocs].
Le site fournit toutes les instructions nécessaires à sa bonne utilisation, mais une rapide présentation des commandes à utiliser est fournie ci-dessous.

### Installation de mkdocs

```bash
sudo pip install mkdocs
```

### Compilation de la documentation

Pour prévisualiser le rendu html, lancer un terminal, aller dans le dossier de la documentation `toad/doc/toad/` et entrer la commande suivante ```mkdocs serve``` puis ouvrez votre navigateur à la page [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Pour compiler la documentation, taper la commande ```mkdocs build --clean```.
La documentation est alors accessible dans le dossier `html`.



[pandoc]: http://johnmacfarlane.net/pandoc/
[tuto]: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet
[mkinfo]: http://blog.wax-o.com/2014/04/tutoriel-un-guide-pour-bien-commencer-avec-markdown/
[mkdocs]: http://www.mkdocs.org/
