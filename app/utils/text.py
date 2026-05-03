import re
import unicodedata


def slugify(value: str) -> str:
    """Lowercase, strip accents, replace non-alphanumerics with single dashes."""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def email_local_part(prenom: str, nom: str) -> str:
    p = slugify(prenom)
    n = slugify(nom)
    if not p or not n:
        return slugify(f"{prenom}{nom}") or "user"
    return f"{p}.{n}"
