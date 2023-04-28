# Créa'IA
Application permettant de créer et d'entraîner vos propres modèles d'intelligence artificielle.

## Installation
Afin de pouvoir utiliser l'application, il est nécessaire d'installer les dépendances situées dans le fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

Vous devez aussi avoir préalablement installé SQLite3 sur votre machine, et de vous assurer que votre version de Python est inférieure ou égale à 3.11.0 et supérieure à 3.9 (>3.11 n'est pas pris en charge par PyTorch).

## Utilisation

Le code source de l'application se trouve dans le dossier `sources/`. Nous avons également mis à disposition dans le dossier `sources/chiens_chats/` un jeu de données de +800 images de chats et de chiens que vous pouvez utiliser pour tester l'application. Toutes les images sont libres de droits et proviennent de Wikimedia Commons.

Pour lancer l'application, vous devez vous rendre dans le dossier `sources/` et exécuter la commande :

```bash
flask run
```

Une fois l'application lancée, vous pouvez vous rendre à l'adresse [127.0.0.1:5000](http://127.0.0.1:5000) pour y accéder.


## Sources externes

Voici une liste de l'ensemble des sources externes que nous avons utilisées pour réaliser ce projet :

- Flask, utilisé pour le serveur web de l'application.
- PyTorch, utilisé pour l'entrainement des modèles d'IA et pour la prédiction.
- resnet18 qui est un modèle de réseau de neurones pré-entrainé pour la classification d'images.
- Toutes les ressources graphiques ont été réalisées dans le cadre de ce projet.
- Les images de chats et de chiens proviennent de Wikimedia Commons et sont libres de droits.