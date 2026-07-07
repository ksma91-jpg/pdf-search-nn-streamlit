import streamlit as st

from services.simple_index import load_simple_index, search_simple_index, build_llm_prompt


st.title("🔍 Búsqueda mejorada")

index = load_simple_index()

if not index:
    st.warning(
        "No existe índice de búsqueda todavía. "
        "Ve a la página Documentos y haz clic en 'Construir índice de búsqueda'."
    )
else:
    st.success(f"Índice cargado: {len(index)} fragmentos disponibles.")

query = st.text_input(
    "Escribe tu búsqueda",
    placeholder="Ejemplo: semaglutida, registro sanitario, evaluación farmacológica...",
)

top_k = st.slider(
    "Número de resultados",
    min_value=5,
    max_value=30,
    value=10,
)

if st.button("Buscar"):
    if not query.strip():
        st.warning("Escribe una consulta.")
    else:
        results = search_simple_index(query, top_k=top_k)

        if not results:
            st.warning("No encontré resultados para esa búsqueda.")
        else:
            st.success(f"Encontré {len(results)} resultados relevantes.")

            st.subheader("Prompt listo para copiar al LLM interno")

            prompt = build_llm_prompt(query, results)

            st.text_area(
                "Copia este bloque y pégalo en el LLM interno aprobado",
                value=prompt,
                height=350,
            )

            st.subheader("Resultados encontrados")

            for i, result in enumerate(results, start=1):
                with st.expander(
                    f"{i}. {result['title']} — página {result['page']} — score {result['score']}",
                    expanded=i <= 3,
                ):
                    st.write(result["text"])
                    st.caption(result["url"])
