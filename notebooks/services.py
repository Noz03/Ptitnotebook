import fitz  # PyMuPDF
import os
import requests
import chromadb
import uuid
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentService:
    # Xử lý tài liệu: Trích xuất văn bản và phân đoạn (chunking).
    @staticmethod
    def process_and_chunk_pdf(file_path, file_name):
        # Đọc tệp PDF, trích xuất văn bản và chia nhỏ nội dung kèm metadata.
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Đường dẫn tệp không tồn tại: {file_path}")

        # Cấu hình bộ chia văn bản (800 ký tự mỗi đoạn, lấy trước 100 ký tự)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
        )

        processed_chunks = []
        try:
            pdf_document = fitz.open(file_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                page_text = page.get_text("text")
                
                if not page_text.strip():
                    continue
                    
                chunks = text_splitter.split_text(page_text)
                for chunk in chunks:
                    processed_chunks.append({
                        "content": chunk,
                        "metadata": {
                            "source": file_name,
                            "page": page_num + 1
                        }
                    })
            pdf_document.close()
            return processed_chunks
        except Exception as e:
            raise Exception(f"Lỗi trong quá trình xử lý PDF: {str(e)}")

class KaggleService:
    # AI server service (Kaggle/Ngrok).
    KAGGLE_API_URL = getattr(settings, 'KAGGLE_API_URL', 'http://localhost:8000')

    @classmethod
    def get_embeddings(cls, texts):
        # Gửi yêu cầu nhúng văn bản tới API.
        try:
            response = requests.post(
                f"{cls.KAGGLE_API_URL}/embed", 
                json={"texts": texts},
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("embeddings", [])
        except Exception as e:
            raise Exception(f"Lỗi kết nối API Embedding: {str(e)}")

    @classmethod
    def get_chat_answer(cls, prompt):
        # Gửi yêu cầu khởi tạo văn bản (Chat/Generation) tới API.
        try:
            response = requests.post(
                f"{cls.KAGGLE_API_URL}/chat",
                json={"prompt": prompt},
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("answer", "")
        except Exception as e:
            raise Exception(f"Lỗi kết nối API Chat: {str(e)}")

class VectorDBService:
    # Quản lý và truy vấn cơ sở dữ liệu Vector (ChromaDB).
    def __init__(self):
        # Kết nối tới dịch vụ ChromaDB
        chroma_host = getattr(settings, 'CHROMA_DB_HOST', 'localhost')
        chroma_port = getattr(settings, 'CHROMA_DB_PORT', 8000)
        self.client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        self.collection = self.client.get_or_create_collection(name="ptitnotebook_collection")

    def save_chunks_to_db(self, chunks_data):
        # Lưu trữ các đoạn văn bản và vector tương ứng vào cơ sở dữ liệu.
        if not chunks_data:
            return

        texts = [chunk["content"] for chunk in chunks_data]
        metadatas = [chunk["metadata"] for chunk in chunks_data]
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # Lấy vector nhúng từ KaggleService
        embeddings = KaggleService.get_embeddings(texts)

        if not embeddings or len(embeddings) != len(texts):
            raise Exception("Dữ liệu vector trả về không khớp với số lượng văn bản.")

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )

    def search_similar_chunks(self, question, selected_sources=None, top_k=5):
        # Tìm kiếm các đoạn văn bản có độ tương đồng cao nhất với câu hỏi.
        # Nhúng câu hỏi thành vector
        question_embedding = KaggleService.get_embeddings([question])[0]

        where_filter = None
        if selected_sources:
            clean_sources = [str(src) for src in selected_sources if str(src).strip()]
            if clean_sources:
                where_filter = {"source": {"$in": clean_sources}}

        # Truy vấn không gian vector với bộ lọc metadata source
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
            where=where_filter
        )
        return results