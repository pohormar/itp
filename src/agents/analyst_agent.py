from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os


class AnalystAgent:
    def __init__(self, llm):
        self.llm = llm
        
        # POPRAWKA: Prawidłowa ścieżka do katalogu głównego projektu
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        prompt_path = os.path.join(base_dir, 'prompts', 'agent1_analyst', 'instructions.md')
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = ChatPromptTemplate.from_template(f.read())

        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def run(self, document: str) -> str:
        """
        Processes the document using the Analyst agent.
        """
        print("Analyst Agent processing...")
        response = self.chain.invoke({"text_to_analyze": document})
        return response 