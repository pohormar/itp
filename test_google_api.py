import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

print("--- Rozpoczynanie testu połączenia z Gemini Chat API ---")

# 1. Załaduj klucz API z pliku .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or len(api_key) < 10:
    print("BŁĄD: Nie znaleziono GEMINI_API_KEY w pliku .env lub jest on pusty. Przerwanie.")
    exit()

print("Klucz API załadowany pomyślnie.")

# 2. Zainicjalizuj model czatu
try:
    llm = ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model="gemini-2.5-pro"
    )
    print("Model czatu 'gemini-2.5-pro' zainicjalizowany.")
except Exception as e:
    print(f"BŁĄD KRYTYCZNY podczas inicjalizacji modelu: {e}")
    exit()

# 3. Spróbuj zadać proste pytanie
test_question = "What is the capital of Poland?"
print(f"Próba zadania pytania: '{test_question}'")
try:
    response = llm.invoke(test_question)
    print("\n--- SUKCES! ---")
    print("Odpowiedź z Gemini API otrzymana pomyślnie.")
    print(f"\nOdpowiedź Gemini: {response.content}")
except Exception as e:
    print("\n--- BŁĄD KRYTYCZNY PODCZAS POŁĄCZENIA ---")
    print("Wystąpił błąd podczas próby wysłania zapytania do modelu czatu.")
    print("Jeśli to błąd typu 'Deadline Exceeded' lub 'Timeout', potwierdza to problemy z wydajnością po stronie Google.")
    print(f"Szczegóły techniczne błędu: {e}")

print("\n--- Test zakończony ---") 