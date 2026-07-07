import streamlit as st

from config import MANIFEST_PATH, LOCAL_DOCUMENTS
from services.manifest_loader import load_manifest
from services.document_downloader import download_pdf
from services.pdf_reader import extract_pdf_pages
from services.simple_index import build_simple_index, load_simple_index


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

        col1, col2 = st.columns(2)

        with col1:
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

        with col2:
            if st.button("Construir índice de búsqueda"):
                with st.spinner("Construyendo índice de búsqueda..."):
                    records = build_simple_index()

                st.success(f"Índice construido con {len(records)} fragmentos.")

        existing_index = load_simple_index()

        if existing_index:
            st.info(f"Índice actual disponible: {len(existing_index)} fragmentos.")
        else:
            st.warning("Todavía no existe índice de búsqueda. Haz clic en Construir índice de búsqueda.")

except Exception as e:
    st.error("Error leyendo el manifiesto.")
    st.exception(e)
