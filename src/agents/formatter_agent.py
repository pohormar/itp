from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.retriever import BaseRetriever
import os

class FormatterAgent:
    def __init__(self, llm):
        self.llm = llm
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        prompt_path = os.path.join(base_dir, 'prompts', 'agent4_qa_formatter', 'instructions.md')
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            # Cały szablon jest ładowany z pliku .md
            self.prompt_template = ChatPromptTemplate.from_template(f.read())

        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def run(self, simplified_text_with_criticism: str, retriever: BaseRetriever) -> str:
        """
        Processes the text using the Formatter agent with RAG context.
        """
        print("Formatter Agent processing with RAG context...")
        
        context_docs = retriever.get_relevant_documents(simplified_text_with_criticism)
        context_str = "\n\n---\n\n".join([doc.page_content for doc in context_docs])
        
        response = self.chain.invoke({
            "context": context_str,
            "simplified_text_with_criticism": simplified_text_with_criticism
        })
        
        return response.strip().removeprefix("```markdown").removeprefix("```").strip()