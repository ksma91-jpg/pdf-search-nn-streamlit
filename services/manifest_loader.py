from pathlib import Path
import pandas as pd


def load_manifest(manifest_path: Path) -> pd.DataFrame:
    if not manifest_path.exists():
        return pd.DataFrame(columns=["title", "url"])

    df = pd.read_csv(manifest_path)

    required_columns = {"title", "url"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"El manifiesto debe contener las columnas: {', '.join(required_columns)}"
        )

    df = df.dropna(subset=["title", "url"])
    df["title"] = df["title"].astype(str).str.strip()
    df["url"] = df["url"].astype(str).str.strip()

    df = df[(df["title"] != "") & (df["url"] != "")]

    return df
