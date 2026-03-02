import argparse
import time
from pathlib import Path

import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tracklist.config import BASE_URL, WAIT_TIMEOUT
from tracklist.driver_factory import build_driver
from tracklist.notifier import (
    get_group_invite_link,
    send_telegram_message,
)
from tracklist.profiles import WATCHLIST_PROFILES
from tracklist.scraper import (
    click_visible_button,
    extract_all_records_from_current_tab,
    get_first_data_row_text,
    wait_until_first_row_changes,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="TrackList - surveillance automatique des records avec watchlist"
    )
    parser.add_argument(
        "--profile",
        choices=sorted(WATCHLIST_PROFILES.keys()),
        required=True,
        help="Profil de watchlist à générer",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=28800,
        help="Intervalle entre deux vérifications en secondes (défaut : 28800 = 8h)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Lance une seule exécution puis s'arrête",
    )

    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval doit être un entier strictement positif.")

    return args


def build_user_watchlist(df: pd.DataFrame, selected_profile: str) -> pd.DataFrame:
    disciplines = WATCHLIST_PROFILES[selected_profile]

    watchlist_df = df[df["discipline"].isin(disciplines)].copy()

    export_df = watchlist_df[
        ["category", "discipline", "performance", "athlete", "country", "date"]
    ].copy()

    export_df = export_df.rename(
        columns={
            "category": "Catégorie",
            "discipline": "Discipline",
            "performance": "Performance",
            "athlete": "Athlète",
            "country": "Pays",
            "date": "Date du record",
        }
    )

    export_df = export_df.sort_values(
        by=["Catégorie", "Discipline", "Date du record"],
        kind="stable",
    ).reset_index(drop=True)

    return export_df


def save_watchlist_html(
    watchlist_df: pd.DataFrame,
    selected_profile: str,
    html_path: Path,
) -> None:
    table_html = watchlist_df.to_html(index=False, classes="watchlist-table", border=0)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>TrackList - Watchlist {selected_profile}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 32px;
            background: #f7f7f7;
            color: #222;
        }}
        h1 {{
            margin-bottom: 8px;
        }}
        p {{
            margin-top: 0;
            color: #555;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        }}
        .watchlist-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        .watchlist-table th,
        .watchlist-table td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        .watchlist-table th {{
            background: #1f4b99;
            color: white;
        }}
        .watchlist-table tr:nth-child(even) {{
            background: #f2f6fc;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>TrackList - Watchlist : {selected_profile}</h1>
        <p>Nombre de records suivis : {len(watchlist_df)}</p>
        {table_html}
    </div>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")


def compare_and_save_watchlist(
    watchlist_df: pd.DataFrame,
    selected_profile: str,
    output_dir: Path,
) -> bool:
    watchlist_csv_path = output_dir / f"{selected_profile}_watchlist.csv"
    watchlist_html_path = output_dir / f"{selected_profile}_watchlist.html"
    alert_path = output_dir / f"{selected_profile}_alerts.txt"

    previous_df = None
    if watchlist_csv_path.exists():
        previous_df = pd.read_csv(watchlist_csv_path, dtype=str).fillna("")

    current_df = watchlist_df.fillna("").astype(str)

    current_df.to_csv(watchlist_csv_path, index=False, encoding="utf-8")
    save_watchlist_html(current_df, selected_profile, watchlist_html_path)

    print(f"\nProfil choisi : {selected_profile}")
    print(f"Nombre de records dans la watchlist : {len(current_df)}")
    print(f"Fichier CSV créé : {watchlist_csv_path}")
    print(f"Fichier HTML créé : {watchlist_html_path}")

    if current_df.empty:
        print("Aucun record trouvé pour ce profil.")
    else:
        print(current_df.to_string(index=False))

    if previous_df is None:
        message = (
            f"Première exécution pour le profil '{selected_profile}'.\n"
            "Aucune comparaison possible pour le moment.\n"
            "La watchlist actuelle a été enregistrée comme référence."
        )
        alert_path.write_text(message, encoding="utf-8")
        print(f"Fichier d'alerte créé : {alert_path}")
        print("Première exécution : aucune comparaison avec un ancien snapshot.")
        return False

    previous_rows = set(previous_df.itertuples(index=False, name=None))
    current_rows = set(current_df.itertuples(index=False, name=None))

    new_rows = current_rows - previous_rows
    removed_rows = previous_rows - current_rows

    lines = [f"Comparaison du profil '{selected_profile}'"]

    if not new_rows and not removed_rows:
        lines.append("Aucun changement détecté.")
        print("Aucun changement détecté par rapport à la dernière exécution.")
        alert_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Fichier d'alerte créé : {alert_path}")
        return False

    if new_rows:
        lines.append("")
        lines.append("Nouveaux records détectés :")
        for row in sorted(new_rows):
            lines.append(" - " + " | ".join(row))

    if removed_rows:
        lines.append("")
        lines.append("Records disparus / modifiés :")
        for row in sorted(removed_rows):
            lines.append(" - " + " | ".join(row))

    print("Changements détectés dans la watchlist.")

    alert_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Fichier d'alerte créé : {alert_path}")

    return True


def run_once(profile: str) -> bool:
    driver = build_driver()

    try:
        output_dir = Path("data")
        output_dir.mkdir(parents=True, exist_ok=True)

        driver.get(BASE_URL)

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
                )
            )
            accept_button.click()

            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "CybotCookiebotDialog"))
            )

            print("Cookies acceptés.")
        except TimeoutException:
            print("Pas de bannière cookies.")

        women_records = extract_all_records_from_current_tab(driver, "Women")
        women_first_row_text = get_first_data_row_text(driver)

        click_visible_button(driver, "Men")
        wait_until_first_row_changes(driver, women_first_row_text)
        men_records = extract_all_records_from_current_tab(driver, "Men")
        men_first_row_text = get_first_data_row_text(driver)

        click_visible_button(driver, "Mixed")
        wait_until_first_row_changes(driver, men_first_row_text)
        mixed_records = extract_all_records_from_current_tab(driver, "Mixed")

        all_records = women_records + men_records + mixed_records
        df = pd.DataFrame(all_records)

        records_path = output_dir / "records.csv"
        df.to_csv(records_path, index=False, encoding="utf-8")

        print("Taille du DataFrame :", df.shape)
        print("Colonnes :", list(df.columns))
        print(f"Fichier CSV créé : {records_path}")

        user_watchlist_df = build_user_watchlist(df, profile)
        alert_detected = compare_and_save_watchlist(
            user_watchlist_df,
            profile,
            output_dir,
        )

        return alert_detected

    finally:
        driver.quit()
        print("\nNavigateur fermé.")


def print_group_info(profile: str) -> None:
    group_link = get_group_invite_link()

    print(f"\nProfil actif : {profile}")

    if group_link:
        print(f"Groupe/canal Telegram des alertes : {group_link}")
        print("Tous les profils enverront leurs alertes dans ce même groupe.")
    else:
        print("Aucun lien de groupe configuré dans tracklist/config.py.")


def monitor_loop(profile: str, interval_seconds: int) -> None:
    alert_path = Path("data") / f"{profile}_alerts.txt"
    cycle_number = 1

    try:
        while True:
            print(f"\n=== Cycle de surveillance #{cycle_number} ===")

            try:
                alert_detected = run_once(profile)

                if alert_detected:
                    print("Alerte détectée. Tentative d'envoi Telegram...")

                    message = f"Changement détecté pour le profil '{profile}'."
                    if alert_path.exists():
                        message = alert_path.read_text(encoding="utf-8")

                    try:
                        send_telegram_message(message)
                        print("Notification Telegram envoyée.")
                    except Exception as exc:
                        print(f"Échec de l'envoi Telegram : {exc}")
                else:
                    print("Aucune alerte à envoyer.")

            except Exception as exc:
                print(f"Erreur pendant le cycle de surveillance : {exc}")

            print(f"Prochaine vérification dans {interval_seconds} secondes...")
            cycle_number += 1
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur. Surveillance stoppée proprement.")


def main() -> None:
    args = parse_args()

    print_group_info(args.profile)

    if args.once:
        run_once(args.profile)
        return

    monitor_loop(args.profile, args.interval)


if __name__ == "__main__":
    main()