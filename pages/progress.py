import streamlit as st
import time
import requests
import json
import sys
import os
import re

# --- Konfiguracja strony i ZABEZPIECZENIE ---
st.set_page_config(layout="wide")

# Ukrycie menu nawigacyjnego (sidebar)
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Sprawdzenie, czy kluczowe stany sesji istnieją.
# Jeśli nie, oznacza to, że użytkownik trafił tu bezpośrednio lub odświeżył stronę.
if "processing" not in st.session_state or "upload_data" not in st.session_state:
    # Bezpieczne przełączenie na stronę główną, jeśli stan jest niekompletny
    st.warning("Sesja wygasła lub brak danych. Przekierowuję na stronę główną...")
    time.sleep(2) # Krótka pauza, aby użytkownik zobaczył wiadomość
    st.switch_page("app.py")

# OSTATECZNE ROZWIĄZANIE PROBLEMU Z IMPORTEM:
# Ręcznie dodajemy główny katalog projektu do ścieżki Pythona.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.ui_utils import apply_global_styles

def reset_to_upload():
    """Resetuje stan sesji i wraca do strony głównej."""
    st.session_state.original_text = ""
    st.session_state.simplified_text = ""
    st.session_state.review_required = False
    st.session_state.uploaded_file_name = None
    st.session_state.processing = False
    st.session_state.checkbox_states = []
    st.session_state.completed_steps = []
    st.session_state.debug_outputs = []
    st.session_state.total_duration = 0 # Inicjalizujemy czas całkowity
    st.switch_page("app.py")

# Aplikuj globalne style
apply_global_styles()

def run_analysis_pipeline(upload_data, timer_placeholder):
    """Uruchamia potok analizy i aktualizuje stan w czasie rzeczywistym."""
    st.session_state.completed_steps = []
    st.session_state.debug_outputs = []
    steps_placeholder = st.empty()
    debug_placeholder = st.empty()

    try:
        api_url = "http://127.0.0.1:8000/process"
        files = {'file': (upload_data['name'], upload_data['bytes'], 'application/pdf')}
        start_time = time.time()

        with st.status("Rozpoczynanie analizy...", expanded=True) as status:
            status.update(label="🔌 Łączenie z serwerem...")
            with requests.post(api_url, files=files, stream=True, timeout=300) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    total_time_so_far = time.time() - start_time
                    timer_placeholder.metric("Całkowity czas", f"{total_time_so_far:.2f} s")
                    update = json.loads(line.decode('utf-8'))
                    
                    # --- PRZEBUDOWANA LOGIKA AKTUALIZACJI ---
                    # Krok 1: Zawsze aktualizuj czas poprzedniego kroku, jeśli jest dostępny
                    if st.session_state.completed_steps and "duration_of_prev" in update:
                        if "⏳" in st.session_state.completed_steps[-1]:
                            duration = update["duration_of_prev"]
                            duration_str = f" **[{duration:.2f}s]**"
                            last_step_text = st.session_state.completed_steps[-1].replace("⏳", "✔️").replace("...", "").strip()
                            st.session_state.completed_steps[-1] = f"{last_step_text}{duration_str}"

                    # Krok 2: Obsłuż bieżący status
                    current_status = update.get("status")
                    if current_status == "in_progress":
                        step_message = f"⏳ {update.get('step')}..."
                        st.session_state.completed_steps.append(step_message)
                        status.update(label=f"Pracuje... {update.get('step')}")
                    
                    elif current_status == "debug":
                        source = update.get("source", "Unknown Agent")
                        output = update.get("output", "No output.")
                        st.session_state.debug_outputs.append((source, output))
                    
                    elif current_status == "error":
                        if st.session_state.completed_steps and "✔️" in st.session_state.completed_steps[-1]:
                            st.session_state.completed_steps[-1] = st.session_state.completed_steps[-1].replace("✔️", "❌")
                        status.update(label="Błąd krytyczny!", state="error", expanded=True)
                        st.session_state.completed_steps.append(f"❌ **Błąd: {update.get('message', '...')}**")
                        # Zapiszmy czas do momentu błędu
                        st.session_state.total_duration = total_time_so_far
                        return 

                    elif current_status == "completed":
                        status.update(label="🎉 Analiza zakończona!", state="complete")
                        st.session_state.completed_steps.append("✔️ **Analiza zakończona!**")
                        st.session_state.total_duration = total_time_so_far
                        # Zapisz finalne wyniki - używamy spójnych kluczy
                        st.session_state.original_text = update.get("original_text", "")
                        st.session_state.final_text = update.get("final_text", "")
                        st.session_state.analyzed_text = update.get("analyzed_text", "")
                        break
                    
                    # Krok 3: Zawsze odświeżaj widok po każdej aktualizacji
                    with steps_placeholder.container(border=True):
                        for step in st.session_state.completed_steps:
                            st.markdown(step)
                    with debug_placeholder.container():
                        for source, output in st.session_state.debug_outputs:
                            with st.expander(f"🕵️‍♂️ Dane debugowania z: **{source}**", expanded=False):
                                st.code(output, language=None)
    
    except requests.exceptions.RequestException as e:
        st.session_state.completed_steps.append(f"❌ Błąd połączenia z serwerem: {e}")
    
    finally:
        st.session_state.processing = False
        # KLUCZOWA POPRAWKA: Jawne polecenie przerysowania interfejsu
        st.rerun()

# --- Główny widok strony ---
_ , col2, _ = st.columns([1, 4, 1])
with col2:
    if st.session_state.get("processing", False):
        st.title("Przetwarzanie dokumentu...")
        if st.button("Anuluj przetwarzanie", use_container_width=True):
            reset_to_upload()
        timer_placeholder = st.empty()
        run_analysis_pipeline(st.session_state.upload_data, timer_placeholder)
    
    else: # Ten blok wykona się czysto po przerysowaniu przez st.rerun()
        st.title("Analiza zakończona")
        st.success(f"🎉 **Przetwarzanie zakończone!** Całkowity czas: **{st.session_state.get('total_duration', 0):.2f}s**")
        
        with st.container(border=True):
            for step in st.session_state.get("completed_steps", []):
                st.markdown(step)
        
        if st.session_state.get("debug_outputs"):
            st.markdown("---")
            st.subheader("Zapisy z przetwarzania (debug)")
            for source, output in st.session_state.get("debug_outputs", []):
                with st.expander(f"🕵️‍♂️ Dane z: **{source}**", expanded=False):
                    st.code(output, language=None)

        # --- PRZYCISK Z LOGIKĄ PRZEKIEROWANIA ---
        if st.button("Zobacz wyniki", use_container_width=True):
            final_text = st.session_state.get("final_text", "")
            
            # Sprawdzamy, czy w finalnym tekście znajdują się tagi wymagające recenzji.
            if re.search(r'\[\[WYMAGA_SPRAWDZENIA\]\]', final_text):
                st.session_state.review_required = True
                st.switch_page("pages/review.py")
            else:
                st.session_state.review_required = False
                st.switch_page("pages/compare.py")

        # Ten blok jest teraz niepotrzebny, ponieważ cała logika jest w powyższych dwóch blokach
        # elif not st.session_state.upload_data:
        #     st.warning("Brak danych do przetworzenia. Proszę wrócić do strony głównej.")
        #     if st.button("Powrót do strony głównej"):
        #         reset_to_upload() 