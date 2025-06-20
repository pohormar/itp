import os
from dotenv import load_dotenv

def load_config(config_path="config.yaml"):
    """Ładuje konfigurację z pliku YAML."""
    import yaml
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Plik konfiguracyjny '{config_path}' nie został znaleziony.")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_api_key_from_env_file(env_file_path=".env") -> str | None:
    """
    Bezpośrednio wczytuje i parsuje plik .env, aby uzyskać GEMINI_API_KEY.
    Omija mechanizm zmiennych środowiskowych, aby zapobiec cachowaniu.
    """
    if not os.path.exists(env_file_path):
        return None
    
    with open(env_file_path, 'r') as f:
        for line in f:
            if line.strip().startswith("GEMINI_API_KEY"):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    # Usuń cudzysłowy, jeśli istnieją
                    return parts[1].strip().strip('"').strip("'")
    return None

def initialize_app_config():
    """
    Inicjalizuje konfigurację aplikacji, ładując plik YAML i zmienne środowiskowe.
    Zwraca główny obiekt konfiguracyjny.
    """
    load_dotenv() # Pozostawiamy dla spójności z innymi częściami (np. ingest.py)
    config = load_config()
    # Tutaj możemy dodać więcej logiki inicjalizacyjnej w przyszłości
    return config 