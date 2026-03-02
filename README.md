
# TrackList

TrackList est un projet Python qui scrape les records du site World Athletics avec Selenium.

Il récupère les données des onglets **Women**, **Men** et **Mixed**, génère une watchlist selon un profil choisi, puis envoie une alerte Telegram si un changement est détecté.

## Objectif

Automatiser la surveillance des records pour éviter de vérifier le site manuellement.


## Utilisation

Lancer le programme :

```bash
python -m tracklist.main --profile sprint
```

Faire une seule exécution :

```bash
python -m tracklist.main --profile sprint --once
```

Sous Windows, si tu lances avec le Python de `.venv` :

```bash
.\.venv\Scripts\python.exe -m tracklist.main --profile sprint
```

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
```

## Données générées

Le programme crée des fichiers dans `data/`, par exemple :

* `records.csv`
* `<profil>_watchlist.csv`
* `<profil>_watchlist.html`
* `<profil>_alerts.txt`




