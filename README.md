
# Plateforme de vote

Ce dépôt contient tout le code source de la plateforme de vote de l'univers associatif de Centrale Lille.

Il permet d'assurer la gestion des élections pour :
- le BDA, le BDE, le BDS et le BDI
- le CA élèves 

Cette plateforme a été initialement développée en 2020 par Jean-Baptiste Caplan (promo 2021). 
Elle tire profit de l'unification des services web de Centrale Lille Associations, notamment en s'appuyant sur le service d'authentification fourni par la plateforme web principale de Centrale Lille Associations.  


## Installation

### Installation des dépendances directes du projet

Après avoir récupéré le code depuis le dépôt GitHub il faut installer les dépendances en utilisant pip, mais avant cela il est recommandé de mettre en place un environnement virtuel avec ``virtualenv`` :
```shell script
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

; CLA_AUTH
CLA_AUTH_HOST=
CLA_AUTH_IDENTIFIER=
```

Prenez soin dans la configuration du projet de bien sélectionner l'environnement de développement (`cla_votes.settings.development`) ou de production (`cla_votes.settings.production`) :
- En définissant une variable d'environnement (par défaut l'environnement de production est utilisé) :
```shell script
DJANGO_SETTINGS_MODULE=cla_votes.settings.development
```
- Directement dans le fichier ``manage.py``
```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cla_votes.settings.development")
```

### Initialisation et mise à jour

Une fois configuré, le projet doit être initialisé. Ce processus correspond à la création des tables dans la base de données ainsi que la préparation des ressources statiques.

Ce processus doit être répété à chaque mise à jour pour que les modifications soient effectivement déployées.

Voici les commandes correspondantes :
 ```shell script
# Utilisation du virtual environment
source venv/bin/activate
# Mise à jour de la base de données
python3 manage.py makemigrations
python3 manage.py migrate
# Déploiement des ressources static
python3 manage.py collectstatic
```

### Configuration d'Apache

L'une des façon de déployer ce project en production est d'utiliser un serveur web, par exemple Apache avec le mod WSGI activé.

Voici un exemple de configuration :

```
<VirtualHost *:80>

    ServerName vote.centralelilleassos.fr

    Alias /static/ /var/www/vote.centralelilleassos.fr/static/

    <Directory /var/www/vote.centralelilleassos.fr/static>
            Require all granted
    </Directory>

    WSGIDaemonProcess vote.centralelilleassos.fr python-home=/var/www/vote.centralelilleassos.fr/venv python-path=/var/www/vote.centralelilleassos.fr
    WSGIProcessGroup vote.centralelilleassos.fr

    WSGIScriptAlias / /var/www/vote.centralelilleassos.fr/cla_votes/wsgi.py process-group=vote.centralelilleassos.fr

    <Directory /var/www/vote.centralelilleassos.fr/cla_votes>
            <Files wsgi.py>
                    Require all granted
            </Files>
    </Directory>

    ErrorLog /var/www/vote.centralelilleassos.fr/error.log
    CustomLog /var/www/vote.centralelilleassos.fr/access.log common

</VirtualHost>
```