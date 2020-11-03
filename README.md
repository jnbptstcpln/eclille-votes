
# Plateforme de vote

Ce dépôt contient tout le code source de la plateforme de vote de l'univers associatif de Centrale Lille.

Il permet d'assurer la gestion des élections pour :
- le BDA, le BDE, le BDS et le BDI
- le CA élèves 

Cette plateforme a été initialement développée en 2020 par Jean-Baptiste Caplan (promo 2021). 
Elle tire profit de l'unification des services web de Centrale Lille Associations, notamment en s'appuyant sur le service d'authentification fourni par la plateforme web principale de Centrale Lille Associations.  


## Installation

### Installation des dépendances directes du projet

Après avoir récupéré le code depuis le dépôt GitHub il faut installer les dépendances en utilisant pip, mais avant cela il est recommandé de mettre en place un environement virtuel avec ``virtualenv`` :
```
virtualenv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Configuration du projet

Avant de lancer le projet, il faut mettre en place la configuration dans ``cla_votes/settings/settings.ini`` en vous appuyant sur le modèle ``settings.sample.ini`` :
```
[settings]
; Project
SECRET_KEY=random_string
ALLOWED_HOSTS=host1,host2,...

; DATABASE
DATABASE_HOST=
DATABASE_PORT=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_NAME=
```

Prenez soin dans la configuration du projet de bien sélectionner l'environement de développement (`cla_votes.settings.development`) ou de production (`cla_votes.settings.production`) :
- En définissant une variable d'environnement :
```
DJANGO_SETTINGS_MODULE=cla_votes.settings.development
```
- Directement dans le fichier ``manage.py``
```
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cla_votes.settings.development")
```
