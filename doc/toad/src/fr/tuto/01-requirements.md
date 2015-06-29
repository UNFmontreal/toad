# Pré-requis

## Compte sur les serveurs UNF

Pour utiliser TOAD au CRIUGM, il faut disposer d’un compte sur les serveurs informatiques de l’unité. 
Ce compte peut être personnel ou celui d’une équipe. 
L’informaticien de l’UNF, [Mathieu Desrosiers](mailto:mathieu.desrosiers@criugm.qc.ca), est en charge de la création et de la gestion de ces comptes.

## Ligne de commande

L’ensemble des outils de TOAD repose sur des commandes à entrer dans un terminal. 
L’introduction à l’usage de la ligne de commande et d’un terminal va au-delà de TOAD. 
Ainsi, nous vous renvoyons à de la documentation externe, par exemple :

- [Tutoriel OpenClassRooms](http://openclassrooms.com/courses/domptez-votre-mac-avec-mac-os-x-mavericks/le-terminal-dans-os-x)

## Utilisation de SSH

L’utilisation de TOAD nécessite une connexion à distance entre votre ordinateur et les serveurs de l’UNF (même si vous utilisez les salles de traitement du centre). 
Il est vivement recommandé d’utiliser le protocole SSH.
Ce dernier est installé par défaut sur les ordinateurs Apple McIntosh et sur les distributions GNU/Linux. 
Pour Windows, nous vous renvoyons à différentes documentations externes :

- [Tutoriel sur CommentCaMarche.net](http://www.commentcamarche.net/faq/80-se-logguer-a-distance-avec-ssh-windows)
- [Tutoriel OpenClassRooms](http://openclassrooms.com/courses/reprenez-le-controle-a-l-aide-de-linux/la-connexion-securisee-a-distance-avec-ssh)
- [Vidéo Youtube en anglais](https://www.youtube.com/watch?v=9CZphjhQxIQ)

## Ajouter TOAD à votre session

### Savoir si TOAD est disponible

Afin de pouvoir utiliser TOAD, vous devez ajouter ses sources à votre session. 
Tout d’abord, connectez-vous à votre session sur un des serveurs du l’UNF :

~~~bash
# Remplacer 'username' par votre identifiant UNF
ssh -Y username@stark.criugm.qc.ca
~~~

Pour savoir si TOAD est déjà disponible, taper la commande suivante :

~~~bash
which toad
~~~

Si la commande retourne un chemin d’accès du genre `/usr/local/toad/...`, vous n’avez rien de plus à faire.
Si la commande ne retourne rien (écran vide), c’est que TOAD n’est pas disponible depuis votre session et que vous devez l’ajouter.

### Ajouter TOAD 

Si vous utilisez TOAD que très occasionnellement, vous pouvez sourcer TOAD *à chaque fois* que vous vous connecter au serveur en tapant la ligne de commande suivante :

~~~bash
source  /usr/local/toad/etc/unf-toad-config.sh
~~~

Sinon, vous pouvez ajouter cette ligne de commande à votre profil de session pour que TOAD soit automatiquement ajouté à votre session à chaque connexion :

1. Ouvrir/Créer le fichier '.bash_profile'

~~~bash
vi ~/.bash_profile
~~~

2. Passer en mode 'édition' pour ajouter du texte en appuyant sur **`i`**

3. Copier cette ligne à la fin du document (sans les guillemets) : 'source  /usr/local/toad/etc/unf-toad-config.sh'

4. Pour sauvegarder et quitter l’éditeur, presser d’abord la touche `échappe (ESC)` puis taper **`:wq`** (ne pas oublier les deux points !)

5. Rafraichir la mémoire de l’ordinateur pour tenir compte de cette modification : 

~~~bash
source ~/.bash_profile
~~~
