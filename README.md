# I Tak Podpiszesz

Aplikacja webowa, która automatyzuje i wspomaga proces upraszczania złożonych dokumentów (np. umów, regulaminów) w formacie PDF. System wykorzystuje potok wyspecjalizowanych agentów AI do analizy, uproszczenia i weryfikacji treści, aby uczynić je bardziej zrozumiałymi dla przeciętnego użytkownika.

## Architektura

*   **Backend:** FastAPI
*   **Frontend:** Streamlit
*   **Orkiestracja AI:** LangChain
*   **Model Językowy:** Google Gemini 1.5 Pro
*   **Baza Wektorowa (RAG):** ChromaDB
*   **Przetwarzanie/Generowanie PDF:** PyMuPDF / xhtml2pdf

## Instalacja

1.  **Sklonuj repozytorium:**
    ```bash
    git clone <adres-repozytorium>
    cd <nazwa-katalogu-projektu>
    ```

2.  **Utwórz plik `.env`:**
    Skopiuj plik `.env.example` (jeśli istnieje) lub utwórz nowy plik o nazwie `.env`. Wewnątrz pliku wklej swój klucz API do Google Gemini:
    ```
    GEMINI_API_KEY="AI..."
    ```

3.  **Utwórz i aktywuj środowisko wirtualne:**
    Zalecane jest użycie Pythona w wersji 3.11+.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    *Ważne: Po aktywacji, na początku linii terminala powinno pojawić się `(.venv)`.*
    *Aby opuścić środowisko wirtualne, użyj polecenia `deactivate`.*

4.  **Zainstaluj zależności Pythona:**
    Upewnij się, że środowisko jest aktywne i użyj poniższej komendy:
    ```bash
    pip install -r requirements.txt
    ```

## Uruchomienie Aplikacji

Aplikacja składa się z dwóch oddzielnych procesów: serwera backendu (FastAPI) i interfejsu użytkownika (Streamlit). **Musisz uruchomić je w dwóch osobnych terminalach.**

### Krok 1: Uruchom serwer Backendu

W pierwszym oknie terminala **aktywuj środowisko wirtualne**, a następnie uruchom serwer.

```bash
# 1. Aktywuj środowisko
source .venv/bin/activate

# 2. Uruchom serwer (użyj 'python', a nie 'python3')
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```
Poczekaj, aż w terminalu pojawi się komunikat `Application startup complete.`. **Nie zamykaj tego terminala.**

### Krok 2: Uruchom interfejs Frontendu

W **drugim, nowym** oknie terminala również **aktywuj środowisko wirtualne**, a następnie uruchom aplikację Streamlit.

```bash
# 1. Aktywuj środowisko w nowym terminalu
source .venv/bin/activate

# 2. Uruchom aplikację Streamlit
streamlit run app.py
```
Aplikacja powinna automatycznie otworzyć się w Twojej przeglądarce, zazwyczaj pod adresem `http://localhost:8501`.

Gotowe! Możesz teraz korzystać z aplikacji. 