
# TrackList

**TrackList** est un projet Python de web scraping réalisé par **Khabous El Mehdi** et **Gazzar Abdellah**.

Le programme surveille les records du site **World Athletics** avec **Selenium**, récupère les données des onglets **Women**, **Men** et **Mixed**, génère une **watchlist** selon un profil choisi, compare les résultats avec les exécutions précédentes, et peut envoyer une **alerte Telegram** en cas de changement.

## Objectif

Automatiser la veille des records World Athletics afin d’éviter une vérification manuelle répétitive du site.

## Fonctionnalités

- Scraping automatisé des records depuis World Athletics
- Parcours des onglets **Women / Men / Mixed**
- Génération du fichier `data/records.csv`
- Génération d’une watchlist selon un profil
- Export en **CSV**, **HTML** et **TXT**
- Comparaison avec la watchlist précédente
- Notification **Telegram** en cas de changement
- Mode exécution unique avec `--once`
- Mode surveillance continue toutes les **8 heures**


## Utilisation

Lancer le programme :

```bash
python -m tracklist.main --profile <type>
```

Faire une seule exécution :

```bash
python -m tracklist.main --profile <type> --once
```

Sous Windows, si tu lances avec le Python de `.venv` :

```bash
.\.venv\Scripts\python.exe -m tracklist.main --profile <type>
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





