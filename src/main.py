import yaml
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import io
import json
from pydantic import BaseModel
import asyncio
import fitz  # PyMuPDF
from src.pipeline import Pipeline
from src.utils.config_utils import load_config
from src.utils.logger import get_logger

# Inicjalizacja loggera dla tego modułu
logger = get_logger(__name__)

app = FastAPI()

# Ładowanie konfiguracji i inicjalizacja potoku
try:
    logger.info("Ładowanie konfiguracji i inicjalizacja potoku przy starcie aplikacji...")
    config = load_config("config.yaml")
    pipeline = Pipeline(config_path="config.yaml")
    logger.info("Aplikacja i potok zostały pomyślnie zainicjalizowane.")
except Exception as e:
    logger.critical(f"Krytyczny błąd podczas inicjalizacji potoku: {e}", exc_info=True)
    pipeline = e

async def stream_pipeline_responses(raw_text: str):
    """
    Asynchronicznie strumieniuje odpowiedzi z potoku jako zdarzenia NDJSON.
    """
    logger.info("Rozpoczęcie strumieniowania odpowiedzi z potoku.")
    if isinstance(pipeline, Exception):
        logger.error(f"Zgłoszono błąd inicjalizacji potoku do klienta: {pipeline}")
        yield json.dumps({'status': 'error', 'message': 'Pipeline initialization failed', 'details': str(pipeline)}) + "\n"
        return
    try:
        async for update_json_str in pipeline.process(raw_text):
            yield update_json_str + "\n"
            await asyncio.sleep(0.01)
    except Exception as e:
        logger.error(f"Błąd podczas strumieniowania z potoku: {e}", exc_info=True)
        error_message = {
            "status": "error",
            "message": "An error occurred during pipeline processing.",
            "details": str(e),
        }
        yield json.dumps(error_message) + "\n"
    logger.info("Zakończono strumieniowanie odpowiedzi z potoku.")

@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    """
    Przetwarza przesłany plik PDF, wyodrębnia tekst i uruchamia potok analizy.
    Zwraca odpowiedź strumieniową z postępem.
    """
    logger.info(f"Otrzymano nowe żądanie przetwarzania pliku: '{file.filename}' (rozmiar: {file.size} bajtów).")

    async def error_streamer(message, details, log_as_error=True):
        if log_as_error:
            logger.error(f"Błąd podczas przetwarzania pliku '{file.filename}': {message} | Szczegóły: {details}")
        else:
            logger.warning(f"Ostrzeżenie podczas przetwarzania pliku '{file.filename}': {message}")
        error_update = {"status": "error", "message": message, "details": details}
        yield json.dumps(error_update) + "\n"

    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            logger.warning(f"Przesłany plik '{file.filename}' jest pusty.")
            return StreamingResponse(
                error_streamer("Przesłany plik jest pusty.", "", log_as_error=False),
                media_type="application/x-ndjson",
            )
        
        logger.info(f"Rozpoczęcie parsowania pliku PDF: '{file.filename}'")
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            raw_text = "".join(page.get_text() for page in doc)
        logger.info(f"Pomyślnie wyodrębniono tekst z pliku '{file.filename}'.")

    except Exception as e:
        return StreamingResponse(
            error_streamer("Nie udało się odczytać lub sparsować pliku PDF.", str(e)),
            media_type="application/x-ndjson",
        )

    if not raw_text.strip():
        return StreamingResponse(
            error_streamer(
                "Wyodrębniony tekst jest pusty. Nie można przetworzyć dokumentu.", "", log_as_error=False
            ),
            media_type="application/x-ndjson",
        )
    
    logger.info(f"Pomyślnie przygotowano dane z '{file.filename}'. Rozpoczynanie potoku analizy.")
    return StreamingResponse(
        stream_pipeline_responses(raw_text), media_type="application/x-ndjson"
    )

if __name__ == "__main__":
    logger.info("Uruchamianie serwera Uvicorn w trybie deweloperskim...")
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True) 