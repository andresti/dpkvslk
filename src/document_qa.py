from typing import Dict
from logging import getLogger
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import LlamaCpp
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import torch
from utils import parse_lines_to_chunks

logger = getLogger(__name__)

class DocumentQA:
    def __init__(
        self,
        model_path: str = "models/phi-2.Q4_K_M.gguf",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        chunk_size: int = 500
    ):
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': device}
        )
        
        self.chunk_size = chunk_size
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]
        )
        
        logger.info(f"Loading model from {model_path}")
        self.llm = LlamaCpp(
            model_path=model_path,
            temperature=0.1,
            max_tokens=1024,
            n_ctx=2048, # Tulenevalt mudelist ei saa suuremat konteksti kasutada
            n_gpu_layers=0,
            verbose=False
        )        
        self._vector_store = None
        self.qa_chain = None

    def load_document(self, file_path: str) -> None:
        """Laadime ja tükeldame dokumendi."""
        chunks = []
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            for p, page in enumerate(pages):
                page_num = page.metadata.get('page_label', page.metadata.get('page', p + 1))
                
                lines = page.page_content.split('\n')
                chunks.extend(parse_lines_to_chunks(lines, page_num, self.chunk_size))
        else:   # Muul juhul eeldame, et see on tekstifail
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()                
                # Tekstifaile käsitleme ühe leheküljena
                chunks.extend(parse_lines_to_chunks(lines, 1, self.chunk_size))
        # Kasutame FAISS-teeki vektorite sarnasusotsingute jaoks
        self._vector_store = FAISS.from_documents(chunks, self.embeddings)
        self._create_qa_chain()
        
    def _create_qa_chain(self) -> None:
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self._vector_store.as_retriever(
                search_kwargs={
                    "k": 3
                },
            ),
            chain_type_kwargs={
                "prompt": self.prompt_template,
            },
            return_source_documents=True
        )

    @property
    def prompt_template(self) -> PromptTemplate:
        prompt_template = """You are a precise and thorough document analysis assistant. Your task is to answer questions about the document using only the provided context. Follow these guidelines:
* Provide detailed but concise answers, around 5 sentences in length, giving the most relevant information.
* If there are multiple relevant points, explain each one
* Use only specific information provided in the context
* If you cannot find the answer in the context or the context is empty, say "I don't know". Never make up an answer.

Context: {context}

Question: {question}

Answer:"""
        return PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

    def answer_question(
        self,
        question: str
    ) -> Dict[str, str]:
        """Küsime vastuse dokumendist."""
        result = self.qa_chain.invoke({"query": question})
        
        answer = result['result']
        # Kogume kokku viidete info ja lisame vastusele
        if 'source_documents' in result and len(result['source_documents']) > 0:
            refs_text = "["
            for i, doc in enumerate(result['source_documents'], 1):
                if doc.metadata["start_line"] == doc.metadata["end_line"]:
                    ref_text = f"Page {doc.metadata['page']}, line {doc.metadata['start_line']}"
                else:
                    ref_text = f"Page {doc.metadata['page']}, lines {doc.metadata['start_line']}-{doc.metadata['end_line']}"
                if len(refs_text) > 1:
                    refs_text += f"; {ref_text}"
                else:
                    refs_text += f"{ref_text}"
            refs_text += "]"
            answer += f" {refs_text}"        
        else:
            return {
                'answer': "I could not find any relevant information in the document to answer this question.",
            }
        return {
            'answer': answer,
        }
