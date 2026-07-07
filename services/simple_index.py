from pathlib import Path
import json
import re

from config import (
    MANIFEST_PATH,
    LOCAL_DOCUMENTS,
    LOCAL_METADATA,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from services.manifest_loader import load_manifest
from services.document_downloader import download_pdf
from services.pdf_reader import extract_pdf_pages
from services.chunker import chunk_text


INDEX_PATH = LOCAL_METADATA / "simple_index.json"


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_simple_index() -> list[dict]:
    manifest = load_manifest(MANIFEST_PATH)
    records = []

    for _, row in manifest.iterrows():
        title = row["title"]
        url = row["url"]

        pdf_path = download_pdf(title, url, LOCAL_DOCUMENTS)
        pages = extract_pdf_pages(pdf_path)

        for page in pages:
            page_number = page["page"]
            page_text = page["text"]

            chunks = chunk_text(
                page_text,
                chunk_size=CHUNK_SIZE,
                overlap=CHUNK_OVERLAP,
            )

            for chunk_index, chunk in enumerate(chunks):
                records.append(
                    {
                        "title": title,
                        "url": url,
                        "pdf_path": str(pdf_path),
                        "page": page_number,
                        "chunk_index": chunk_index,
                        "text": chunk,
                        "text_normalized": normalize_text(chunk),
                    }
                )

    LOCAL_METADATA.mkdir(parents=True, exist_ok=True)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)

    return records


def load_simple_index() -> list[dict]:
    if not INDEX_PATH.exists():
        return []

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def search_simple_index(query: str, top_k: int = 10) -> list[dict]:
    query = query.strip()

    if not query:
        return []

    records = load_simple_index()

    if not records:
        return []

    query_normalized = normalize_text(query)
    terms = [term for term in query_normalized.split(" ") if term]

    results = []

    for record in records:
        text = record["text_normalized"]

        exact_score = text.count(query_normalized) * 5
        term_score = sum(text.count(term) for term in terms)

        score = exact_score + term_score

        if score > 0:
            result = dict(record)
            result["score"] = score
            results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]
