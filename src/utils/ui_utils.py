import streamlit as st
import base64
import re

# Definicje kolorów dla podświetlania tagów
COLOR_SIMPLIFY = "#e8f5e9"  # Jasny zielony
COLOR_REVIEW = "#e7f3fe"   # Jasny niebieski
COLOR_ERROR = "#ffebee"    # Jasny czerwony

def display_header(title: str, subtitle: str):
    """Wyświetla standardowy nagłówek strony."""
    st.title(title)
    st.markdown(f"**{subtitle}**")
    st.divider()

def display_analysis_results(original_text, simplified_text):
    """Wyświetla wyniki analizy w dwóch kolumnach."""
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Oryginalny Tekst")
        st.text_area("Oryginał", original_text, height=500, key="original_text_display", disabled=True)
    with col2:
        st.subheader("Tekst Uproszczony")
        st.text_area("Uproszczony", simplified_text, height=500, key="simplified_text_display", disabled=True)

def get_download_button(data: bytes, label: str, file_name: str, mime: str) -> None:
    """
    Renderuje przycisk pobierania pliku w Streamlit.

    Args:
        data (bytes): Dane pliku do pobrania w formie bajtów.
        label (str): Etykieta przycisku.
        file_name (str): Domyślna nazwa pliku po pobraniu.
        mime (str): Typ MIME pliku.
    """
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True
    )

def apply_global_styles():
    """Aplikuje globalne style CSS do całej aplikacji Streamlit."""
    
    # Wybrany kolor: neutralny, jasnoszary
    NEUTRAL_COLOR = "#F0F2F6"  # Jasnoszary, standardowy dla UI
    NEUTRAL_COLOR_HOVER = "#E1E4E8" # Ciemniejszy szary dla efektu hover
    BORDER_COLOR = "#BCC0C4"
    
    # CSS do wstrzyknięcia
    styles = f"""
    <style>
        /* Celowanie w główny przycisk (primary) */
        div[data-testid="stButton"] > button {{
            background-color: {NEUTRAL_COLOR};
            color: #31333F; /* Ciemniejszy tekst dla czytelności */
            border: 1px solid {BORDER_COLOR};
        }}
        /* Efekt hover dla głównego przycisku */
        div[data-testid="stButton"] > button:hover {{
            background-color: {NEUTRAL_COLOR_HOVER};
            border: 1px solid {BORDER_COLOR};
            color: #31333F;
        }}
        
        /* Celowanie w przycisk pobierania (stDownloadButton) */
        div[data-testid="stDownloadButton"] > button {{
            background-color: {NEUTRAL_COLOR};
            color: #31333F;
            border: 1px solid {BORDER_COLOR};
        }}
        /* Efekt hover dla przycisku pobierania */
        div[data-testid="stDownloadButton"] > button:hover {{
            background-color: {NEUTRAL_COLOR_HOVER};
            border: 1px solid {BORDER_COLOR};
            color: #31333F;
        }}
    </style>
    """
    st.markdown(styles, unsafe_allow_html=True)

def highlight_tags(text: str) -> str:
    """Zamienia niestandardowe tagi na formatowanie HTML z kolorami."""
    if not isinstance(text, str): return ""
    
    # 1. Zamień tagi uproszczenia na <span...>
    text = text.replace("<simplify>", f'<span style="background-color: {COLOR_SIMPLIFY};">')
    text = text.replace("</simplify>", "</span>")

    # 2. Zamień tagi wymagające sprawdzenia na <span...>
    text = text.replace("[[WYMAGA_SPRAWDZENIA]]", f'<span style="background-color: {COLOR_REVIEW};">')
    text = text.replace("[[/WYMAGA_SPRAWDZENIA]]", "</span>")

    # 3. Zamień tagi błędów na <span...>
    text = text.replace("[[BLAD_LOGICZNY]]", f'<span style="background-color: {COLOR_ERROR};">')
    text = text.replace("[[/BLAD_LOGICZNY]]", "</span>")
    
    # 4. Usuń tagi <legal_def>
    text = re.sub(r'</?legal_def>', '', text)

    return text 