import re
from pathlib import Path


def safe_filename(name: str, default: str = "legal_document") -> str:
    """
    Convert a document name into a safe filename.
    """

    if not name or not name.strip():
        return default

    filename = name.strip()

    filename = re.sub(
        r"[^\w\s-]",
        "",
        filename,
        flags=re.UNICODE,
    )

    filename = re.sub(
        r"\s+",
        "_",
        filename,
    )

    filename = re.sub(
        r"_+",
        "_",
        filename,
    )

    filename = filename.strip("._-")

    if not filename:
        return default

    return filename[:100]


def clean_text(text: str) -> str:
    """
    Clean unnecessary whitespace while preserving paragraphs.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = [
        line.rstrip()
        for line in text.split("\n")
    ]

    return "\n".join(lines).strip()


def ensure_directory(path: str) -> Path:
    """
    Create a directory if it does not already exist.
    """

    directory = Path(path)
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory