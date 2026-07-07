from pathlib import Path
import json
import re
import unicodedata

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


def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_text(text: str) -> str:
    text = text.lower()
    text = remove_accents(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_query(query: str) -> list[str]:
    query = normalize_text(query)
    tokens = re.findall(r"\b\w+\b", query)

    stopwords = {
        "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas",
        "y", "o", "en", "para", "por", "con", "sin", "sobre", "que", "se",
        "a", "al", "es", "son", "como", "cual", "cuál", "cuando", "donde",
        "qué", "quien", "quién"
    }

    return [token for token in tokens if token not in stopwords and len(token) > 2]


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


def score_record(query: str, record: dict) -> float:
    query_normalized = normalize_text(query)
    query_terms = tokenize_query(query)
    text = record["text_normalized"]
    title = normalize_text(record["title"])

    score = 0.0

    # Frase exacta completa
    if query_normalized and query_normalized in text:
        score += 50

    # Frase exacta en título
    if query_normalized and query_normalized in title:
        score += 25

    # Coincidencias por término
    for term in query_terms:
        term_count = text.count(term)
        title_count = title.count(term)

        score += term_count * 4
        score += title_count * 8

        # Bonus si el término aparece cerca del inicio del fragmento
        first_position = text.find(term)
        if first_position != -1:
            if first_position < 200:
                score += 3
            elif first_position < 500:
                score += 1

    # Bonus por cubrir varios términos de la consulta
    if query_terms:
        matched_terms = sum(1 for term in query_terms if term in text)
        coverage = matched_terms / len(query_terms)
        score += coverage * 20

    return score


def search_simple_index(query: str, top_k: int = 10) -> list[dict]:
    query = query.strip()

    if not query:
        return []

    records = load_simple_index()

    if not records:
        return []

    results = []

    for record in records:
        score = score_record(query, record)

        if score > 0:
            result = dict(record)
            result["score"] = round(score, 2)
            results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]


def build_context_from_results(results: list[dict], max_chars: int = 8000) -> str:
    context_parts = []
    total_chars = 0

    for idx, result in enumerate(results, start=1):
        source = (
            f"[Fuente {idx}] "
            f"{result['title']} — página {result['page']}"
        )

        text = result["text"]

        block = f"{source}\n{text}\n"

        if total_chars + len(block) > max_chars:
            break

        context_parts.append(block)
        total_chars += len(block)

    return "\n---\n".join(context_parts)


def build_llm_prompt(question: str, results: list[dict]) -> str:
    context = build_context_from_results(results)

    prompt = f"""Necesito responder la siguiente pregunta usando únicamente el contexto proporcionado.

Pregunta:
{question}

Contexto:
{context}

Instrucciones:
- Responde únicamente con base en el contexto.
- Si el contexto no contiene evidencia suficiente, dilo claramente.
- Cita siempre las fuentes usando el nombre del documento y la página.
- No inventes información.
- Resume la respuesta de forma clara y estructurada.
"""

    return prompt
