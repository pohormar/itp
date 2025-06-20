from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os


class CriticAgent:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        
        # POPRAWKA: Prawidłowa ścieżka do katalogu głównego projektu
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        prompt_path = os.path.join(base_dir, 'prompts', 'agent2_criticality_validator', 'instructions.md')

        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = ChatPromptTemplate.from_template(f.read())
        
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def run(self, original_text: str, simplified_text: str) -> str:
        """
        Processes the texts using the Critic agent.
        """
        print("Critic Agent processing...")
        # Użycie przekazanego retrievera
        relevant_docs = self.retriever.get_relevant_documents(simplified_text)
        # Sformatowanie kontekstu do stringa
        rag_context_str = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])

        response = self.chain.invoke({
            "original_text": original_text,
            "simplified_text": simplified_text
        })
        return response 