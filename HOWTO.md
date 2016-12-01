# Prérequis

machine virtuelle (idéalement linux)

Python3

pip3

virtualenv

# Création de l'environnement virtual env

virtualenv -p python3 env

# Switcher vers l'environnement virtuel

source env/bin/activate


# Installation des dépendances

pip -r requirements.txt

# Téléchargement et indexation de la base BAN

python update.py url_ban
