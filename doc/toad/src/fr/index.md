<img src="figs/toad_logo.png" alt="Toad logo" style="width: 450px;"/>

# TOolkit d’Analyse de Diffusion (TOAD)

Bienvenue sur la documentation en français de [TOAD](http://unf-montreal.ca/toad/).
Les sources de TOAD, ainsi que les instructions d’installation sont disponibles sur [Github](https://github.com/UNFmontreal/toad).

TOAD offre une chaine de traitements automatisés des images de diffusion (DWI/DTI). 
Les différentes étapes de traitement permettent :

1. Nettoyer les données
2. Préparer les masques de substance blanche et substance grise
3. Définir les faisceaux
4. Extraire automatiquement les principales métriques (FA, MD...)

**Merci de consulter la section [*Conditions d’utilisation*](about/license.md) pour connaître les conditions d’utilisation de TOAD auxquelles vous devez souscrire !**

Cette documentation vous propose un rapide [tutoriel](tuto/01-requirements.md) pour démarrer TOAD ainsi qu’une documentation plus complète (en anglais seulement) décrivant chacune des étapes de TOAD (outils utilisés, paramètres choisis...).

Le tutoriel est également disponible au format PDF pour simplifier sa lecture :

- [Tutoriel (français)](../../Toad_Tuto_fr.pdf)
- [Tutoriel (anglais)](../../Toad_Tuto_en.pdf)

Nous vous conseillons également de **consulter [cette page](tuto/00-refs.md)** afin de vous familiariser avec les techniques d’analyse utilisées dans TOAD.


## L’équipe

<img src="figs/JDoyon.jpg" alt="Julien Doyon" style="width: 50px;"/> **Julien Doyon** : directeur scientifique de l’[UNF (Unité de Neuroimagerie Fonctionnelle)](www.unf-montreal.ca)

<img src="figs/SBrambati.jpg" alt="Simona Brambati" style="width: 50px;"/> **Simona Brambati** : chercheuse et responsable scientifique du projet

<img src="figs/ABore.jpg" alt="Arnaud Boré" style="width: 50px;"/> **Arnaud Boré** : développeur et responsable scientifique du projet

<img src="figs/MDesrosiers.jpg" alt="Mathieu Desrosiers" style="width: 50px;"/> **Mathieu Desrosiers** : développeur principal et mainteneur du projet

<img src="figs/CBedetti.jpg" alt="Christophe Bedetti" style="width: 50px;"/> **Christophe Bedetti** : développeur et responsable de l’évaluation qualité 

<img src="figs/GVallet.jpg" alt="Guillaume Vallet" style="width: 50px;"/>  **Guillaume Vallet** : responsable de la documentation et du site internet

<img src="figs/JChen.jpg" alt="Jeni Chen" style="width: 50px;"/> **Jeni Chen** : traduction et documentation du projet

<img src="figs/BPinsard.jpg" alt="Basile Pinsard" style="width: 50px;"/> **Basile Pinsard** : développeur et conseiller scientifique

<img src="figs/AHanganu.jpg" alt="Alexandru Hanganu" style="width: 50px;"/> **Alexandru Hanganu** : conseiller scientifique


## Mot du directeur

L’exploration in vivo de la connectivité structurale du cerveau et de la moelle épinière, de façon non-invasive grâce à l’imagerie de diffusion, est devenue aujourd’hui un incontournable tant en clinique que dans de nombreux domaines des neurosciences fondamentales. Toutefois, l’analyse des données provenant de cette technique de l’imagerie par résonance magnétique demeure encore complexe et peu standardisée. Résultant d’un travaille d’équipe exceptionnel, la présente plateforme nommée « Toolkit for Analysis of Diffusion MRI (TOAD) » offre aux utilisateurs novices et experts une gamme d’outils faciles d’utilisation qui permettent de vérifier et visualiser, étape-par-étape, les résultats obtenus suite au pré-traitement des images et à l’analyse statistique des diverses métriques d’anisotropie et de tractographie.

A titre de Directeur Scientifique de l’Unité de Neuroimagerie Fonctionnelle (UNF) du Centre de recherche de l’Institut universitaire de gériatrie de Montréal (CRIUGM), c’est avec fierté que je remercie toute l’équipe de professionnels de recherche, étudiants et chercheurs qui, ensemble, ont permis la création de TOAD.  Je crois sincèrement que cette dernière sera non seulement utile pour les cliniciens-nnes, mais pour la communauté scientifique du Québec, du Canada et d’ailleurs dans le monde.

Julien Doyon, Ph.D.
Directeur scientifique
Unité de Neuroimagerie Fonctionnelle

Directeur
Réseau de Bio-Imagerie du Québec

## Introduction à TOAD (diapositives)

<iframe src="http://slides.com/toadunfcriugm/deck-2/embed" width="576" height="420" scrolling="no" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

*Note :* Vous pouvez naviguer verticalement tel qu'indiqué par les flèches bleues.

## [Contact](about/contact.md)

Vous pouvez nous contacter directement par courriel : [**toadunf.criugm@gmail.com**](toadunf.criugm@gmail.com).

**Pour toute question**, merci d’indiquer dans l’*objet du message* le nom de la tâche et/ou de la section entre crochet suivi de votre question, tel que `[denoising] comment changer l’algorithme ?` ou encore `[website] information manquante`.
