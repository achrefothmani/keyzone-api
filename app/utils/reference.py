import secrets

PREFIX = "P"
STARTING_REFERENCE_NUMBER = 1000


def format_reference(number: int) -> str:
    """Format a number into the property reference format P<number>."""
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Number must be a positive integer")
    return f"{PREFIX}{number}"


def generate_reference() -> str:
    """Fallback generator - we will likely phase this out or keep for generic use."""
    suffix = secrets.token_hex(3).upper()
    return f"{PREFIX}-{suffix}"
