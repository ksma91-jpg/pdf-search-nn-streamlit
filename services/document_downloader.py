from pathlib import Path
from urllib.parse import urlparse
import hashlib
import requests


def safe_filename(title: str, url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name

    if not name.lower().endswith(".pdf"):
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        name = f"{title}_{digest}.pdf"

    cleaned = (
        name.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace("?", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
    )

    return cleaned


def download_pdf(title: str, url: str, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = safe_filename(title, url)
    target_path = target_dir / filename

    if target_path.exists() and target_path.stat().st_size > 0:
        return target_path

    headers = {
        "User-Agent": "Mozilla/5.0 NN-PDF-Search/1.0"
    }

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").lower()

    if "pdf" not in content_type and not url.lower().endswith(".pdf"):
        raise ValueError(
            f"La URL no parece ser un PDF. Content-Type: {content_type}"
        )

    target_path.write_bytes(response.content)

    return target_path
