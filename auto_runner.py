import argparse
import subprocess
import sys
import time
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Relance automatiquement TrackList à intervalle régulier."
    )
    parser.add_argument(
        "--profile",
        default="sprint",
        help=(
            "Nom du profil de watchlist à transmettre à tracklist.main "
            "(ex: sprint, road, jumps, etc.)"
        ),
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=3,
        help="Nombre d'heures entre deux exécutions (défaut : 3).",
    )

    args = parser.parse_args()

    if args.hours <= 0:
        parser.error("--hours doit être strictement positif.")

    return args


def run_tracklist(watchlist_profile: str) -> int:
    command = [
        sys.executable,
        "-m",
        "tracklist.main",
        "--profile",
        watchlist_profile,
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 60)
    print(f"[{now}] Lancement de TrackList")
    print(f"Profil de watchlist demandé : {watchlist_profile}")
    print("Commande :", " ".join(command))

    result = subprocess.run(command)

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{end_time}] Exécution terminée avec code retour : {result.returncode}")

    return result.returncode


def main() -> None:
    args = parse_args()
    interval_seconds = int(args.hours * 60 * 60)
    cycle_number = 1

    print("Auto-runner démarré.")
    print(f"Profil de watchlist : {args.profile}")
    print(f"Intervalle : {args.hours} heure(s)")
    print("Le scraping complet sera relancé automatiquement.")
    print("Appuie sur Ctrl+C pour arrêter.\n")

    try:
        while True:
            print(f"--- Cycle #{cycle_number} ---")
            run_tracklist(args.profile)

            print(
                f"Prochaine exécution dans {interval_seconds} seconde(s) "
                f"({args.hours} heure(s))."
            )

            cycle_number += 1
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur. Auto-runner stoppé proprement.")


if __name__ == "__main__":
    main()