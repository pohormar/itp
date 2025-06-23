import os
import yaml
import chromadb
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

# --- Adapter ---
# Ta klasa rozwiązuje problem z niekompatybilną "wtyczką" (sygnaturą metody).
class ChromaDBEmbeddingFunctionAdapter(EmbeddingFunction):
    """
    Adapter dostosowujący starszą funkcję embeddingu z LangChain
    do interfejsu oczekiwanego przez nowsze wersje ChromaDB.
    """
    def __init__(self, langchain_embedding_function: GoogleGenerativeAIEmbeddings):
        self._langchain_embedding_function = langchain_embedding_function

    # Ta metoda ma idealną sygnaturę, której oczekuje ChromaDB 0.5+
    def __call__(self, input: Documents) -> Embeddings:
        # W środku po prostu wywołujemy oryginalną funkcję z LangChain
        print(f"    - Osadzanie {len(input)} fragmentów przez adapter...")
        return self._langchain_embedding_function.embed_documents(input)

def main():
    """
    Główna funkcja do tworzenia statycznych baz wiedzy w ChromaDB
    na podstawie plików zdefiniowanych w config.yaml.
    """
    print("--- Rozpoczęcie procesu tworzenia statycznych baz wiedzy (ingestion) ---")
    load_dotenv()

    # 1. Załaduj konfigurację
    try:
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        chroma_config = config.get('chromadb', {})
        print("Konfiguracja załadowana pomyślnie.")
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku config.yaml. Przerwanie.")
        return

    # 2. Zainicjalizuj komponenty
    db_path = chroma_config.get('path', 'chroma_db')
    collections_config = chroma_config.get('collections', {})
    embedding_model_name = chroma_config.get('embedding_model')
    api_key = os.getenv("GEMINI_API_KEY")

    if not all([db_path, collections_config, embedding_model_name, api_key]):
        print("BŁĄD: Brak kluczowych informacji w config.yaml lub zmiennej GEMINI_API_KEY. Przerwanie.")
        return

    try:
        chroma_client = chromadb.PersistentClient(path=db_path)
        google_embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=api_key,
            model=embedding_model_name
        )
        # Tworzymy naszą "przejściówkę", opakowując oryginalną funkcję
        embedding_function = ChromaDBEmbeddingFunctionAdapter(google_embeddings)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        print("Komponenty ChromaDB, Google i TextSplitter zainicjalizowane pomyślnie.")
    except Exception as e:
        print(f"BŁĄD KRYTYCZNY podczas inicjalizacji komponentów: {e}")
        return
    
    # 3. Przetwórz każdą kolekcję
    knowledge_base_path = "knowledge_base"
    for collection_name, filenames in collections_config.items():
        if collection_name == 'main':
            continue

        print(f"\n--- Przetwarzanie kolekcji: {collection_name} ---")
        
        try:
            chroma_client.delete_collection(name=collection_name)
            print(f"Istniejąca kolekcja '{collection_name}' została usunięta.")
        except ValueError:
            print(f"Kolekcja '{collection_name}' nie istniała, zostanie stworzona od nowa.")
        
        # Przekazujemy naszą idealnie dopasowaną przejściówkę do ChromaDB
        collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )

        all_docs, all_ids = [], []
        for filename in filenames:
            file_path = os.path.join(knowledge_base_path, filename)
            if not os.path.exists(file_path):
                print(f"  - OSTRZEŻENIE: Plik '{filename}' nie został znaleziony. Pomijanie.")
                continue

            print(f"  - Wczytywanie i dzielenie pliku: {filename}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = text_splitter.split_text(content)
            print(f"    - Podzielono na {len(chunks)} fragmentów.")
            
            all_docs.extend(chunks)
            all_ids.extend([f"{collection_name}-{filename}-{i}" for i in range(len(chunks))])
        
        if not all_docs:
            print("Brak dokumentów do przetworzenia w tej kolekcji.")
            continue

        try:
            print(f"Dodawanie {len(all_docs)} fragmentów do kolekcji '{collection_name}'...")
            collection.add(
                documents=all_docs,
                ids=all_ids
            )
            print("  - SUKCES: Dane zostały zapisane w ChromaDB.")
        except Exception as e:
            print(f"\nBŁĄD KRYTYCZNY podczas dodawania do kolekcji '{collection_name}': {e}")
            print("Pominięto tę kolekcję.\n")
            continue

    print("\n--- Proces tworzenia statycznych baz wiedzy zakończony. ---")

if __name__ == "__main__":
    main()