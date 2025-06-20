from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.retriever import BaseRetriever
import os


class SimplifierAgent:
    def __init__(self, llm):
        self.llm = llm
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        prompt_path = os.path.join(base_dir, 'prompts', 'agent3_simplifier', 'instructions.md')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = ChatPromptTemplate.from_template(f.read())

        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def run(self, text_to_simplify: str, retriever: BaseRetriever) -> str:
        """
        Upraszcza tekst, korzystając z kontekstu dostarczonego przez retriever z bazy wiedzy.
        """
        print("Simplifier Agent processing with RAG context...")
        
        context_docs = retriever.get_relevant_documents(text_to_simplify)
        context_str = "\n\n---\n\n".join([doc.page_content for doc in context_docs])
        
        response = self.chain.invoke({
            "context": context_str,
            "text_to_simplify": text_to_simplify
        })
        return response 