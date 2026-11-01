"""App Streamlit. Carga resultados precalculados; solo llama al motor en la pestaña Probador."""

import streamlit as st

from src.config import cargar_config
from src.engine import procesar  # noqa: F401  única puerta al motor; se usará en Probador

cfg = cargar_config()

st.set_page_config(page_title=cfg["app"]["titulo"], layout="wide")
st.title(cfg["app"]["titulo"])

tab_metodo, tab_corpus, tab_resultados, tab_probador = st.tabs(cfg["app"]["pestanas"])

with tab_metodo:
    st.info("Pendiente: el problema, por qué el celular no basta y el pipeline.")

with tab_corpus:
    st.info("Pendiente: reproductor de audio con la transcripción al lado.")

with tab_resultados:
    st.info("Pendiente: capa de transcripción (WER, CER) y capa de registro, por separado.")

with tab_probador:
    st.info("Pendiente: subir un clip y ver transcripción, registro y campos verificados.")
