import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from tracklist.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_BOT_USERNAME,
    TELEGRAM_GROUP_CHAT_ID,
    TELEGRAM_GROUP_INVITE_LINK,
)


TOKEN_PLACEHOLDER = "REMPLACE_ICI_PAR_LE_TOKEN_DU_BOT"
GROUP_CHAT_ID_PLACEHOLDER = "REMPLACE_ICI_PAR_LE_CHAT_ID_DU_GROUPE"
GROUP_LINK_PLACEHOLDER = "REMPLACE_ICI_PAR_LE_LIEN_DU_GROUPE"


def _build_api_url(method: str, **params) -> str:
    token = TELEGRAM_BOT_TOKEN.strip()

    if not token or token == TOKEN_PLACEHOLDER:
        raise RuntimeError(
            "Le token Telegram n'est pas configuré. "
            "Renseigne TELEGRAM_BOT_TOKEN dans tracklist/config.py."
        )

    query = urlencode(params)
    return f"https://api.telegram.org/bot{token}/{method}?{query}"


def _get_json(url: str) -> dict:
    try:
        with urlopen(url, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except HTTPError as exc:
        raise RuntimeError(f"Erreur HTTP Telegram : {exc}") from exc
    except URLError as exc:
        raise RuntimeError(f"Erreur réseau Telegram : {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Réponse Telegram invalide (JSON illisible).") from exc


def _call_telegram_api(method: str, **params) -> dict:
    url = _build_api_url(method, **params)
    payload = _get_json(url)

    if not payload.get("ok"):
        raise RuntimeError(f"Réponse Telegram en erreur : {payload}")

    return payload


def get_group_chat_id() -> str | None:
    value = str(TELEGRAM_GROUP_CHAT_ID).strip()

    if not value or value == GROUP_CHAT_ID_PLACEHOLDER:
        return None

    return value


def get_group_invite_link() -> str | None:
    value = str(TELEGRAM_GROUP_INVITE_LINK).strip()

    if not value or value == GROUP_LINK_PLACEHOLDER:
        return None

    return value


def send_telegram_message(message: str) -> None:
    """
    Envoie le message dans le groupe/canal Telegram unique.
    """
    chat_id = get_group_chat_id()

    if chat_id is None:
        raise RuntimeError(
            "Aucun chat_id de groupe Telegram configuré. "
            "Renseigne TELEGRAM_GROUP_CHAT_ID dans tracklist/config.py."
        )

    _call_telegram_api(
        "sendMessage",
        chat_id=chat_id,
        text=message,
    )


def get_bot_username() -> str:
    return TELEGRAM_BOT_USERNAME