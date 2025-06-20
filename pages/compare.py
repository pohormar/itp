import streamlit as st
import sys
import os
import re
from src.utils.ui_utils import get_download_button, apply_global_styles, highlight_tags, COLOR_SIMPLIFY, COLOR_REVIEW, COLOR_ERROR
from src.utils.pdf_utils import create_pdf_from_html
from markdown_it import MarkdownIt

# --- Konfiguracja ścieżek i importów ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# --- Konfiguracja strony ---
st.set_page_config(layout="wide")
apply_global_styles()
st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    .stMetric { text-align: center; }
    .document-view h1 { font-size: 1.5em; }
    .document-view h2 { font-size: 1.3em; }
    .document-view h3 { font-size: 1.1em; }
    .document-view h4, .document-view h5, .document-view h6 { font-size: 1em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Funkcje pomocnicze ---
def clean_for_pdf(text):
    """Usuwa wszystkie tagi formatujące na potrzeby generowania czystego PDF."""
    if not isinstance(text, str): return ""
    text = re.sub(r'</?simplify>', '', text)
    text = re.sub(r'\[\[/?WYMAGA_SPRAWDZENIA\]\]', '', text)
    text = re.sub(r'\[\[/?BLAD_LOGICZNY\]\]', '', text)
    return text

# --- Główna logika strony ---
st.title("Porównanie dokumentów")
st.markdown("Po lewej stronie znajduje się wersja oryginalna dokumentu, a po prawej wersja przetworzona przez AI.")

original_text = st.session_state.get("original_text", "")
final_text = st.session_state.get("final_text", "")

if not original_text or not final_text:
    st.error("Błąd: Brak danych do porównania. Proszę wrócić do strony głównej i spróbować ponownie.")
    if st.button("⬅️ Wróć do strony głównej"):
        st.switch_page("app.py")
    st.stop()

# --- Statystyki i Legenda ---
col1_s, col2_s = st.columns([1,1])
with col1_s:
    st.subheader("Statystyki Analizy")
    errors_found = final_text.count('[[BLAD_LOGICZNY]]')
    checks_required = final_text.count('[[WYMAGA_SPRAWDZENIA]]')
    st.info(f"Fragmentów oznaczonych do sprawdzenia: **{checks_required}**")
    st.error(f"Wykrytych błędów logicznych: **{errors_found}**")

with col2_s:
    st.subheader("Legenda")
    # Używamy globalnie zdefiniowanych kolorów
    legend_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: {COLOR_SIMPLIFY}; margin-right: 10px; border: 1px solid #ccc;"></div>
        <span>Fragment uproszczony przez AI</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width: 20px; height: 20px; background-color: {COLOR_REVIEW}; margin-right: 10px; border: 1px solid #ccc;"></div>
        <span>Fragment wymagający Twojej weryfikacji</span>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="width: 20px; height: 20px; background-color: {COLOR_ERROR}; margin-right: 10px; border: 1px solid #ccc;"></div>
        <span>Błąd logiczny (uproszczenie niespójne z kontekstem)</span>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

st.markdown("---")

# --- Widok dwóch kolumn ---
col1, col2 = st.columns(2)
with col1:
    st.header("Oryginał")
    md_oryginal = MarkdownIt()
    html_oryginal = md_oryginal.render(original_text)
    st.markdown(f'<div class="document-view" style="height: 600px; overflow-y: scroll; border: 1px solid #e6e6e6; padding: 10px; border-radius: 5px;">{html_oryginal}</div>', unsafe_allow_html=True)

with col2:
    st.header("Wersja AI")
    # Krok 1: Zamień nasze niestandardowe tagi na tagi <span> z odpowiednimi kolorami.
    text_with_highlights = highlight_tags(final_text)
    
    # Krok 2: Użyj `markdown-it-py`, aby przekonwertować markdown na HTML.
    # Ta biblioteka poprawnie zinterpretuje znaki markdown (np. `#`)
    # i jednocześnie zignoruje istniejące tagi HTML (nasze spany).
    md = MarkdownIt()
    html_output = md.render(text_with_highlights.strip())
    
    st.markdown(f'<div class="document-view" style="height: 600px; overflow-y: scroll; border: 1px solid #e6e6e6; padding: 10px; border-radius: 5px;">{html_output}</div>', unsafe_allow_html=True)

# --- Przyciski pobierania i nawigacji ---
st.markdown("---")
col1_b, _, col2_b = st.columns([3, 5, 3])
with col1_b:
    md = MarkdownIt()
    cleaned_markdown = clean_for_pdf(final_text)
    html_content = md.render(cleaned_markdown)
    simplified_pdf_bytes = create_pdf_from_html(html_content)
    
    get_download_button(
        data=simplified_pdf_bytes,
        label="Pobierz Uproszczony (PDF)",
        file_name=f"simplified_{st.session_state.get('uploaded_file_name', 'document.pdf')}",
        mime="application/pdf"
    )

with col2_b:
    if st.button("Przeanalizuj kolejny dokument", use_container_width=True):
        st.switch_page("app.py") 