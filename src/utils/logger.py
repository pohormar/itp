import logging
import sys

def get_logger(name: str):
    """
    Konfiguruje i zwraca logger o podanej nazwie z kolorowym formatowaniem.
    """
    # Definicja kolorów dla różnych poziomów logowania
    COLORS = {
        'DEBUG': '\033[94m',    # Niebieski
        'INFO': '\033[92m',     # Zielony
        'WARNING': '\033[93m',  # Żółty
        'ERROR': '\033[91m',    # Czerwony
        'CRITICAL': '\033[91m\033[1m', # Pogrubiony czerwony
        'RESET': '\033[0m'      # Reset do domyślnego koloru
    }

    class ColoredFormatter(logging.Formatter):
        """Niestandardowy formatter do dodawania kolorów do logów."""
        def format(self, record):
            log_level_color = COLORS.get(record.levelname, COLORS['RESET'])
            record.levelname = f"{log_level_color}{record.levelname:8s}{COLORS['RESET']}"
            record.name = f"\033[95m{record.name:15s}\033[0m" # Fioletowy dla nazwy loggera
            return super().format(record)

    # Sprawdzenie, czy logger ma już handlery (aby uniknąć duplikacji)
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG) # Ustawiamy najniższy poziom, aby przechwytywać wszystkie logi

    # Handler do wyświetlania logów w konsoli
    handler = logging.StreamHandler(sys.stdout)
    
    # Użycie naszego kolorowego formattera
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Zapobiegamy propagacji logów do roota, aby uniknąć podwójnego logowania
    logger.propagate = False
    
    return logger

# Przykładowe użycie, jeśli plik zostanie uruchomiony bezpośrednio
if __name__ == '__main__':
    test_logger = get_logger(__name__)
    test_logger.debug("To jest wiadomość debugowa.")
    test_logger.info("To jest informacja.")
    test_logger.warning("To jest ostrzeżenie.")
    test_logger.error("To jest błąd.")
    test_logger.critical("To jest błąd krytyczny.") 