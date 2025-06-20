import streamlit as st
import sys
import os
import re
from src.utils.ui_utils import apply_global_styles

# --- Konfiguracja ścieżek i importów ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Konfiguracja strony ---
st.set_page_config(layout="wide")
apply_global_styles()
st.markdown("<style>[data-testid='stSidebarNav'] { display: none; }</style>", unsafe_allow_html=True)

# --- Funkcje pomocnicze ---
def extract_tagged_fragments(text):
    """Wyodrębnia fragmenty oznaczone jako błędy lub wymagające sprawdzenia."""
    errors = re.findall(r'\[\[BLAD_LOGICZNY\]\](.*?)\[\[/BLAD_LOGICZNY\]\]', text, re.DOTALL)
    reviews = re.findall(r'\[\[WYMAGA_SPRAWDZENIA\]\](.*?)\[\[/WYMAGA_SPRAWDZENIA\]\]', text, re.DOTALL)
    return errors, reviews

# --- Inicjalizacja stanu sesji ---
if "final_text" not in st.session_state or not st.session_state.final_text:
    st.warning("Brak danych do recenzji. Proszę rozpocząć proces od nowa.")
    if st.button("Powrót do strony głównej"):
        st.switch_page("app.py")
    st.stop()

# --- Główna logika strony ---
st.title("Recenzja fragmentów oznaczonych przez AI")
st.info("Proszę przejrzeć i potwierdzić poniższe fragmenty. Przejście dalej jest możliwe po zaznaczeniu wszystkich pozycji.")

# Ekstrakcja danych i tworzenie listy obiektów
errors_found, reviews_required = extract_tagged_fragments(st.session_state.final_text)
all_items = [{'type': 'error', 'text': item.strip()} for item in errors_found] + \
            [{'type': 'review', 'text': item.strip()} for item in reviews_required]

# Inicjalizacja stanu zaznaczeń
if 'review_checks' not in st.session_state or len(st.session_state.review_checks) != len(all_items):
    st.session_state.review_checks = [False] * len(all_items)

# --- Wyświetlanie liczników i przycisku "Zaznacz wszystko" ---
col1, col2, col3 = st.columns([2,2,3])
with col1:
    st.metric("Błędy logiczne", len(errors_found))
with col2:
    st.metric("Do weryfikacji", len(reviews_required))
with col3:
    st.write("") # Dla wyrównania
    st.write("") # Dla wyrównania
    select_all = st.checkbox("Zaznacz wszystko", value=all(st.session_state.review_checks))

# Aktualizacja stanu na podstawie "Zaznacz wszystko"
if select_all:
    st.session_state.review_checks = [True] * len(all_items)
# Jeśli "Zaznacz wszystko" zostało właśnie odznaczone przez użytkownika
elif all(st.session_state.review_checks) and not select_all:
     st.session_state.review_checks = [False] * len(all_items)


st.markdown("---")

# --- Wyświetlanie listy fragmentów ---
if not all_items:
    st.success("Nie znaleziono żadnych fragmentów wymagających ręcznej recenzji.")
else:
    for i, item_data in enumerate(all_items):
        item_type = item_data['type']
        raw_text = item_data['text']
        
        item_color = "tomato" if item_type == 'error' else "orange"
        
        # Usuń wszystkie tagi (HTML i specjalne), aby wyświetlić czysty tekst
        clean_text = re.sub(r'<[^>]+>|\[\[.*?\]\]', '', raw_text).strip()
        
        st.markdown(f"""
        <div style="border-left: 4px solid {item_color}; padding-left: 10px; margin-bottom: 10px;">
            <p style="margin: 0;">{clean_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.review_checks[i] = st.checkbox(
            "Potwierdzam, że zapoznałem/am się z tym fragmentem", 
            key=f"check_{i}",
            value=st.session_state.review_checks[i]
        )
        st.markdown("---")


# --- Przycisk nawigacji ---
all_checked = all(st.session_state.review_checks)

if st.button("Przejdź do widoku porównania", use_container_width=True, disabled=not all_checked):
    st.switch_page("pages/compare.py")

if not all_checked and all_items:
    st.warning("Musisz zaznaczyć wszystkie powyższe elementy, aby kontynuować.") 