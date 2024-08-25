import chardet
import time
# from langchain_ollama.llms import OllamaLLM
from config import Config as cfg
from rag.vectordb import VectorDB
from utils import clean_text, normalize_documents
from qa_system.qa_manager import KnowledgeBaseSystem
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from rag.rag_prompts import domain_detection, domain_check
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader, WebBaseLoader
# from langchain.chains.summarize import load_summarize_chain
# import PyPDF2

# from langchain.chains import AnalyzeDocumentChain
# import sys, pathlib, pymupdf

    
LOADERS_TYPES = {
    ".pdf": PyMuPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
    "url": WebBaseLoader,
}

class ChatPDF:
    print("rag.py - ChatPDF")
    
    def __init__(self):
        print("rag.py - ChatPDF - __init__()")

        self.json_llm = ChatOllama(model=cfg.MODEL, format= cfg.MODEL_FORMAT, temperature=cfg.MODEL_TEMPERATURE) 
        # self.llm = OllamaLLM(model=cfg.MODEL, temperature=cfg.MODEL_TEMPERATURE, num_ctx=5000) 
        self.knowledge_base_system = KnowledgeBaseSystem()
        self.vector_db = VectorDB()
        self.domain = None
        self.retriever = None
        self.domain_checking = domain_check | self.json_llm | JsonOutputParser()
        self.summary_domain_chain = domain_detection | self.json_llm | JsonOutputParser()
    
    
    def detect_encoding(self,file_path):
        print("rag.py - detect_encoding()")
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
        

    def ingest(self, sources: dict):
        print("rag.py - ingest()")
        print("\n--- INGEST DATA ---")
        start_time = time.time()
        source_extension = sources['source_extension']

        if source_extension not in LOADERS_TYPES:
            raise Exception("Not valid upload source!!")

        if source_extension == "url":
            docs = LOADERS_TYPES[source_extension](sources["url"]).load()
        elif source_extension == ".txt":
            encoding = self.detect_encoding(sources["file_path"])
            print(f"\nDetected encoding: {encoding}")
            
            # Load the file using the detected encoding
            docs = LOADERS_TYPES[source_extension](sources["file_path"], encoding=encoding).load()
        else:
            docs = LOADERS_TYPES[source_extension](sources["file_path"]).load()
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size= cfg.SPLITTER_CHUNK_SIZE,
            chunk_overlap= cfg.SPLITTER_CHUNK_OVERLAP,
            length_function=len,
        )
        
        chunks = clean_text(docs, sources['file_name'])
        chunks = normalize_documents(chunks)
        chunks = self.text_splitter.split_documents(chunks)
        
        try:
            result = self.summary_domain_chain.invoke({"documents": chunks})
        
            print("\nResult data domain detection: ")
            print("\nSummary:    {}".format(result["summary"]))
            print("\nDomain:     {}".format(result["domain"]))
        except Exception as e:
            print(f"Error: {e}. Result data domain detection failed.")
            return "no"
        
        try:
            result = self.domain_checking.invoke({"domain": sources['domain'], "summary": result["summary"], "doc_domain": result["domain"]})  
            print("Result for summary: ", result)
            print("\nDocument in the domain:   {}".format("Yes" if result['score'] == "yes" else "No"))
            
            if result["score"] == "no":
                return result["score"]
        except Exception as e:
            print(f"Error: {e}. Document in the domain failed.")
            return "no"
        
        self.vector_db.add_documents(chunks)
        if not self.retriever:
            self.retriever = self.vector_db.as_retriever()
            print("Retriever set")
            self.knowledge_base_system.set_retriever(self.retriever)
        
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nExecution time: {execution_time:.2f} seconds")
            

    def ask(self, query: str):
        print("rag.py - ask()")
        if self.domain is None:
            return "Please set the domain before asking questions."
        
        try:
            state = self.invoke({"question": query, "domain": self.domain})
        
            if state["question_type"] == "yes":
                response = state["answer"]['answer']
                metadata = state["answer"]['metadata']
                calculation = state["answer"]['calculation']
                return f"{response}\n\nMetadata: {metadata} \n\nCalculation: {calculation}"
            elif state["question_type"] == "no":                
                response = state["answer"]['answer']
                metadata = state["answer"]['metadata']
                return f"{response}\n\nMetadata: {metadata}"
            else:
                return "Question classification failed."
            
        except KeyError as e:
            print(f"KeyError: {e}. The expected structure might be missing or altered.")
            return "There was an issue retrieving the answer. The response structure might be incorrect."
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "An unexpected error occurred."
        
    
    def invoke(self, state):
        print("rag.py - invoke()")
        return self.knowledge_base_system.invoke(state)

    
    def set_domain(self, domain: str):
        print("rag.py - set_domain()")
        self.domain = domain
        
        