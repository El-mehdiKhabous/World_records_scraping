# TrackList

TrackList est un projet Python de web scraping qui surveille les records du site World Athletics à l’aide de Selenium. Un projet réalisé par Khabous El Mehdi et Gazzar Abdellah

Le programme récupère les données des onglets **Women**, **Men** et **Mixed**, génère une watchlist selon un profil choisi, compare les résultats avec les exécutions précédentes et envoie une alerte Telegram en cas de changement.

## Objectif

L’objectif du projet est d’automatiser une veille sur les records World Athletics afin d’éviter une vérification manuelle répétitive du site.

## Fonctionnalités

- Scraping des records depuis World Athletics
- Parcours des onglets Women / Men / Mixed
- Génération d’un fichier `data/records.csv`
- Génération d’une watchlist par profil
- Export de fichiers CSV, HTML et TXT
- Comparaison avec la watchlist précédente
- Notification Telegram en cas de changement
- Mode exécution unique avec `--once`
- Mode surveillance continue toutes les 8 heures

## Structure du projet

```text
tracklist/
├── config.py
├── driver_factory.py
├── profiles.py
├── scraper.py
├── notifier.py
├── main.py

└── auto_runner.py

Utilisation

Lancer le programme :

python -m tracklist.main --profile sprint

Faire une seule exécution :

python -m tracklist.main --profile sprint --once

Sous Windows, si tu lances avec le Python de .venv :

.\.venv\Scripts\python.exe -m tracklist.main --profile sprint
Dépendances

selenium

python-dotenv

Structure du projet
tracklist/
├── config.py
├── driver_factory.py
├── profiles.py
├── scraper.py
├── notifier.py
├── main.py
└── auto_runner.py


## Utilisation

Lancer le programme :

python -m tracklist.main --profile sprint

Faire une seule exécution :

python -m tracklist.main --profile sprint --once

Sous Windows, si tu lances avec le Python de .venv :

.\.venv\Scripts\python.exe -m tracklist.main --profile sprint


## Données générées

Le programme crée des fichiers dans data/, par exemple :

records.csv

<profil>_watchlist.csv

<profil>_watchlist.html

<profil>_alerts.txt
