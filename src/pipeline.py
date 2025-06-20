import json
import uuid
import asyncio
import time
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from src.agents.analyst_agent import AnalystAgent
from src.agents.simplifier_agent import SimplifierAgent
from src.agents.formatter_agent import FormatterAgent
from src.agents.critic_agent import CriticAgent
from .utils.config_utils import get_api_key_from_env_file, load_config
from .utils.logger import get_logger

# Inicjalizacja loggera dla tego modułu
logger = get_logger(__name__)

class Pipeline:
    def __init__(self, config_path="config.yaml"):
        logger.info("Inicjalizacja potoku (pipeline)...")
        self.config = load_config(config_path)
        self.api_key = get_api_key_from_env_file()
        if not self.api_key:
            logger.critical("Nie znaleziono GEMINI_API_KEY w pliku .env!")
            raise ValueError("Nie znaleziono GEMINI_API_KEY w pliku .env lub plik nie istnieje.")
        self._initialize_models()
        self._initialize_retrievers()
        self._initialize_agents()
        logger.info("Potok (pipeline) zainicjalizowany pomyślnie.")

    def _initialize_models(self):
        logger.info("Inicjalizacja modeli językowych...")
        llm_config = self.config['llm']
        self.main_model = ChatGoogleGenerativeAI(
            model=llm_config['main_model'],
            google_api_key=self.api_key,
            temperature=llm_config.get('temperature', 0.1),
            convert_system_message_to_human=True 
        )
        self.validator_model = ChatGoogleGenerativeAI(
            model=llm_config['validator_model'],
            google_api_key=self.api_key,
            temperature=llm_config.get('temperature', 0.1),
            convert_system_message_to_human=True
        )
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=self.config['chromadb']['embedding_model'],
            google_api_key=self.api_key
        )
        logger.info("Modele językowe zainicjalizowane.")

    def _initialize_retrievers(self):
        """Inicjalizuje trwałe retrievery do statycznych baz wiedzy."""
        logger.info("Inicjalizacja retrieverów baz wiedzy...")
        try:
            db_path = self.config.get('chromadb', {}).get('path', 'chroma_db')
            
            # Retriever dla SimplifierAgent
            self.simplifier_retriever = Chroma(
                persist_directory=db_path,
                embedding_function=self.embedding_model,
                collection_name="simplifier"
            ).as_retriever()
            
            # Retriever dla FormatterAgent
            self.formatter_retriever = Chroma(
                persist_directory=db_path,
                embedding_function=self.embedding_model,
                collection_name="formatter"
            ).as_retriever()

            logger.info("Retrievery baz wiedzy zainicjalizowane pomyślnie.")
        except Exception as e:
            logger.critical(f"Nie udało się zainicjalizować retrieverów: {e}", exc_info=True)
            raise

    def _initialize_agents(self):
        logger.info("Inicjalizacja agentów...")
        self.analyst_agent = AnalystAgent(llm=self.main_model)
        self.simplifier_agent = SimplifierAgent(llm=self.main_model)
        self.formatter_agent = FormatterAgent(llm=self.main_model)
        logger.info("Agenci zainicjalizowani.")
        # CriticAgent jest inicjalizowany dynamicznie wewnątrz `process`

    async def process(self, text_input: str):
        request_id = uuid.uuid4()
        logger.info(f"Rozpoczęcie przetwarzania dla żądania: {request_id}")
        vectorstore = None
        collection_name = ""
        
        step_start_time = time.monotonic()
        
        try:
            # --- Krok 1: Inicjalizacja i RAG ---
            step_message = "Inicjalizacja i tworzenie bazy wektorowej (RAG)"
            logger.info(f"[{request_id}] Krok: {step_message}")
            yield json.dumps({"status": "in_progress", "step": step_message})
            
            collection_name = f"rag_{request_id.hex}"
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            docs = text_splitter.create_documents([text_input])
            vectorstore = Chroma.from_documents(
                documents=docs, embedding=self.embedding_model, collection_name=collection_name
            )
            retriever = vectorstore.as_retriever()
            critic_agent = CriticAgent(llm=self.validator_model, retriever=retriever)
            logger.debug(f"[{request_id}] Baza wektorowa '{collection_name}' utworzona pomyślnie.")
            duration = time.monotonic() - step_start_time
            step_start_time = time.monotonic()

            # --- Krok 2: AnalystAgent ---
            step_message = "Analiza wstępna (AnalystAgent)"
            logger.info(f"[{request_id}] Krok: {step_message}")
            yield json.dumps({"status": "in_progress", "step": step_message, "duration_of_prev": duration})
            analysis_result = self.analyst_agent.run(text_input)
            logger.debug(f"[{request_id}] Wynik z AnalystAgent: {analysis_result[:200]}...")
            yield json.dumps({"status": "debug", "source": "AnalystAgent", "output": str(analysis_result)})
            duration = time.monotonic() - step_start_time
            step_start_time = time.monotonic()

            # --- Krok 3: SimplifierAgent ---
            step_message = "Upraszczanie tekstu (SimplifierAgent)"
            logger.info(f"[{request_id}] Krok: {step_message}")
            yield json.dumps({"status": "in_progress", "step": step_message, "duration_of_prev": duration})
            simplified_result = self.simplifier_agent.run(
                text_to_simplify=analysis_result, 
                retriever=self.simplifier_retriever
            )
            logger.debug(f"[{request_id}] Wynik z SimplifierAgent: {simplified_result[:200]}...")
            yield json.dumps({"status": "debug", "source": "SimplifierAgent", "output": str(simplified_result)})
            duration = time.monotonic() - step_start_time
            step_start_time = time.monotonic()

            # --- Krok 4: CriticAgent ---
            step_message = "Krytyka i walidacja (CriticAgent)"
            logger.info(f"[{request_id}] Krok: {step_message}")
            yield json.dumps({"status": "in_progress", "step": step_message, "duration_of_prev": duration})
            critic_result = critic_agent.run(original_text=text_input, simplified_text=simplified_result)
            logger.debug(f"[{request_id}] Wynik z CriticAgent: {critic_result[:200]}...")
            yield json.dumps({"status": "debug", "source": "CriticAgent", "output": str(critic_result)})
            duration = time.monotonic() - step_start_time
            step_start_time = time.monotonic()

            # --- Krok 5: FormatterAgent ---
            step_message = "Formatowanie finalnej odpowiedzi (FormatterAgent)"
            logger.info(f"[{request_id}] Krok: {step_message}")
            yield json.dumps({"status": "in_progress", "step": step_message, "duration_of_prev": duration})
            final_result = self.formatter_agent.run(
                simplified_text_with_criticism=critic_result,
                retriever=self.formatter_retriever
            )
            logger.debug(f"[{request_id}] Wynik z FormatterAgent: {final_result[:200]}...")
            yield json.dumps({"status": "debug", "source": "FormatterAgent", "output": str(final_result)})
            duration = time.monotonic() - step_start_time

            # --- Zakończenie ---
            final_payload = {
                "status": "completed",
                "original_text": text_input,
                "analyzed_text": analysis_result,
                "final_text": final_result,
                "duration_of_prev": duration
            }
            logger.info(f"[{request_id}] Przetwarzanie zakończone pomyślnie.")
            yield json.dumps(final_payload)

        except Exception as e:
            logger.error(f"[{request_id}] Wystąpił krytyczny błąd w potoku: {e}", exc_info=True)
            yield json.dumps({"status": "error", "message": str(e), "details": "Szczegóły błędu zostały zarejestrowane w logach serwera."})
        finally:
            if vectorstore and collection_name:
                try:
                    logger.info(f"[{request_id}] Rozpoczynanie czyszczenia kolekcji RAG '{collection_name}'...")
                    vectorstore.delete_collection()
                    logger.info(f"[{request_id}] Kolekcja RAG '{collection_name}' została pomyślnie usunięta.")
                except Exception as e:
                    logger.warning(f"[{request_id}] Błąd podczas próby czyszczenia kolekcji RAG '{collection_name}': {e}")