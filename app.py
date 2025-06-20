import streamlit as st
import os
import sys

# Dodajemy główny katalog projektu do ścieżki, aby moduły z `src` były widoczne.
# To jest konieczne, gdy uruchamiamy app.py jako skrypt główny.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.utils.pdf_utils import extract_text_from_pdf
from src.utils.ui_utils import apply_global_styles

def initialize_session_state():
    """Inicjalizuje wszystkie klucze stanu sesji przy pierwszym uruchomieniu."""
    keys = [
        'original_text', 'simplified_text', 'uploaded_file_name', 
        'analyzed_text', 'final_text', 'upload_data'
    ]
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = None if key != 'original_text' else ""

    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'completed_steps' not in st.session_state:
        st.session_state.completed_steps = []
    if 'debug_outputs' not in st.session_state:
        st.session_state.debug_outputs = []


# --- Główna logika aplikacji ---
st.set_page_config(
    page_title="I Tak Podpiszesz",
    layout="wide"
)

# Aplikuj globalne style
apply_global_styles()

# Ukrycie menu nawigacyjnego (sidebar)
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

initialize_session_state()

# --- Widok Wgrywania Pliku ---
_ , col2, _ = st.columns([1, 3, 1]) 
with col2:
    st.title("I Tak Podpiszesz")
    st.markdown("##### Przeanalizuj i uprość dowolny dokument PDF za pomocą AI")

    uploaded_file = st.file_uploader(
        "Wybierz plik PDF do analizy", 
        type="pdf", 
        key="pdf_uploader"
    )

    if uploaded_file:
        # Przetwarzamy plik tylko raz, przy zmianie pliku
        if st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            with st.spinner("Przetwarzanie pliku PDF..."):
                st.session_state.original_text = extract_text_from_pdf(uploaded_file.getvalue())
            st.success("Plik PDF został pomyślnie wczytany.")

        # Zawsze pokazuj expander, jeśli tekst jest dostępny
        if st.session_state.original_text:
            with st.expander("Pokaż / Ukryj tekst oryginalny"):
                st.text_area(
                    "Oryginał", 
                    st.session_state.original_text, 
                    height=300, 
                    key="original_text_display"
                )

            st.markdown("---")
            if st.button("🚀 Uruchom Analizę i Uproszczenie", use_container_width=True, type="primary"):
                st.session_state.processing = True
                st.session_state.completed_steps = []
                st.session_state.debug_outputs = []
                st.session_state.upload_data = {"name": uploaded_file.name, "bytes": uploaded_file.getvalue()}
                st.switch_page("pages/progress.py")
    else:
        # Reset stanu, jeśli plik zostanie odłączony
        initialize_session_state() 