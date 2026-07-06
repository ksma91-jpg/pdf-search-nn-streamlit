from pathlib import Path


APP_NAME = "NN PDF Search"

MANIFEST_PATH = Path("documents_manifest.csv")

LOCAL_CACHE = Path("local_cache")
LOCAL_DOCUMENTS = LOCAL_CACHE / "documents"
LOCAL_METADATA = LOCAL_CACHE / "metadata"
LOCAL_TEMP = LOCAL_CACHE / "temp"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

TOP_K_FINAL = 8

for path in [
    LOCAL_CACHE,
    LOCAL_DOCUMENTS,
    LOCAL_METADATA,
    LOCAL_TEMP,
]:
    path.mkdir(parents=True, exist_ok=True)
