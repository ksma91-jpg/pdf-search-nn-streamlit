import streamlit as st

from config import MANIFEST_PATH, LOCAL_DOCUMENTS
from services.manifest_loader import load_manifest
from services.document_downloader import download_pdf
from services.pdf_reader import extract_pdf_pages


st.title("📄 Documentos públicos")

st.caption(
    "Los documentos se leen desde documents_manifest.csv. "
    "La app descarga copias temporales para procesarlas."
)

try:
    manifest = load_manifest(MANIFEST_PATH)

    st.metric("Documentos en manifiesto", len(manifest))

    if manifest.empty:
        st.warning("El archivo documents_manifest.csv no tiene documentos.")
    else:
        st.dataframe(manifest, use_container_width=True)

        if st.button("Descargar y probar lectura de PDFs"):
            total_pages = 0

            progress = st.progress(0)
            status = st.empty()

            for idx, row in manifest.iterrows():
                title = row["title"]
                url = row["url"]

                status.write(f"Procesando: {title}")

                try:
                    pdf_path = download_pdf(title, url, LOCAL_DOCUMENTS)
                    pages = extract_pdf_pages(pdf_path)
                    total_pages += len(pages)

                    st.success(
                        f"OK: {title} — {len(pages)} páginas con texto"
                    )

                except Exception as e:
                    st.error(f"Error procesando {title}: {e}")

                progress.progress((idx + 1) / len(manifest))

            status.write("Proceso terminado.")
            st.info(f"Total de páginas con texto extraídas: {total_pages}")

except Exception as e:
    st.error("Error leyendo el manifiesto.")
    st.exception(e)
