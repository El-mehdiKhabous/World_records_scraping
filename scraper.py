from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tracklist.config import WAIT_TIMEOUT


def clean_text(element) -> str:
    return " ".join(element.text.split())


def get_first_data_row_text(driver) -> str:
    rows = driver.find_elements(By.TAG_NAME, "tr")
    if len(rows) > 1:
        return clean_text(rows[1])
    return ""


def extract_all_records_from_current_tab(driver, category_label: str):
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "tr")) > 1
    )

    rows = driver.find_elements(By.TAG_NAME, "tr")
    data_rows = rows[1:]  # on saute l'en-tête

    records = []

    for row in data_rows:
        cells = row.find_elements(By.TAG_NAME, "td")

        if len(cells) < 9:
            continue

        record = {
            "category": category_label,
            "discipline": clean_text(cells[0]),
            "progression": clean_text(cells[1]),
            "performance": clean_text(cells[2]),
            "wind": clean_text(cells[3]),
            "athlete": clean_text(cells[4]),
            "dob": clean_text(cells[5]),
            "country": clean_text(cells[6]),
            "venue": clean_text(cells[7]),
            "date": clean_text(cells[8]),
        }

        records.append(record)

    return records


def click_visible_button(driver, label: str) -> None:
    buttons = driver.find_elements(By.TAG_NAME, "button")
    target_button = None

    for button in buttons:
        if button.is_displayed() and button.text.strip() == label:
            target_button = button
            break

    if target_button is None:
        raise RuntimeError(f"Bouton '{label}' introuvable ou non visible.")

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        target_button
    )
    driver.execute_script("arguments[0].click();", target_button)


def wait_until_first_row_changes(driver, previous_text: str) -> None:
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "tr")) > 1
        and get_first_data_row_text(d) != previous_text
    )
