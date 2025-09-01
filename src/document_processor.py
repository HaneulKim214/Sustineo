import fitz  # pymupdf
import logging
import os
import PyPDF2
import pytesseract
import re
import numpy as np
from PIL import Image
import io

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Dict

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process PDF documents for RAG-based querying"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        ## Improvements: We could pass in dictionary of text splitters types to handle different types of documents.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001"
                                                       , google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.vector_stores = {}
        
        # Initialize OCR if available
        self.ocr_available = True if pytesseract.get_tesseract_version() else False
    
    def _extract_text_with_ocr(self, page) -> str:
        """Extract text from page using OCR if regular text extraction fails"""
        # Get page as image
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Extract text using OCR
        text = pytesseract.image_to_string(img)
        return text

    
    def _is_scanned_page(self, page) -> bool:
        """Detect if a page is scanned (has images but no text)"""
        text = page.get_text().strip()
        images = page.get_images()
        
        # Page is considered scanned if it has images but very little text
        return len(images) > 0 and len(text) < 25
    
    def process_pdf(self, pdf_path: str, doc_name: str) -> FAISS:
        """Extract and vectorize PDF content with OCR support for scanned pages"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            total_pages = len(doc)
            
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                
                # Check if page is scanned and needs OCR
                if self._is_scanned_page(page):
                    if self.ocr_available:
                        ocr_text = self._extract_text_with_ocr(page)
                        if ocr_text.strip():
                            page_text = ocr_text
                        else:
                            logger.warning(f"OCR failed on page {page_num + 1}")
                    else:
                        logger.warning(f"OCR not available for scanned page {page_num + 1}")
                
                page_text = self._clean_text(page_text)
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
            if doc_name.startswith("peer"):
                output_filename = f"data/processed/{doc_name}_text.txt"
                with open(output_filename, "w") as f:
                    f.write(text)
                    logger.info(f"Extracted text written to {output_filename}")

            # Split into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Add metadata
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": doc_name,
                        "chunk_id": i,
                        "total_chunks": len(chunks) + 1,
                    }
                })
            
            # Create vector store
            texts = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
            )
            
            self.vector_stores[doc_name] = vector_store
            logger.info(f"Processed {doc_name}, vector_store successfully created with {doc_name} key | {len(chunks)} chunks created")
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\-.,;:!?()]', '', text)
        return text.strip()
    
    def query_documents(self, query: str, doc_name: str = None, k: int = 5) -> List[Dict]:
        """Query vector store for relevant chunks"""
        store = self.vector_stores[doc_name]
        results = store.similarity_search_with_score(query, k=k)
        return [{
            "content": doc.page_content,
            "source": doc.metadata.get("source", doc_name),
            "score": score
        } for doc, score in results]