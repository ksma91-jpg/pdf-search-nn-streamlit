import streamlit as st

from config import APP_NAME, LOCAL_CACHE


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 NN PDF Search")
st.caption("Búsqueda inteligente de documentos PDF para uso compartido del equipo")

st.markdown(
    """
    Esta aplicación permitirá:

    - subir documentos PDF;
    - guardarlos en una carpeta compartida de Teams / SharePoint;
    - indexarlos para búsqueda clásica;
    - indexarlos para búsqueda semántica;
    - consultar documentos por significado;
    - mostrar fuentes con archivo y página.
    """
)

col1, col2, col3 = st.columns(3)

col1.metric("Modo", "Streamlit")
col2.metric("Storage", "Teams / SharePoint")
col3.metric("IA", "Búsqueda semántica")

st.info(
    "En los siguientes pasos conectaremos esta app con la carpeta compartida "
    "que ya creaste en Teams."
)

with st.expander("Estado local temporal"):
    st.write(f"Carpeta cache local: `{LOCAL_CACHE}`")
