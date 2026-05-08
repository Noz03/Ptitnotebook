# CHI TIẾT HỆ THỐNG PTITNOTEBOOK

**Tiêu đề**: PtitNotebook - Phần mềm hỏi đáp dựa trên tài liệu được cung cấp
**Trường**: Học viện Công nghệ Bưu chính Viễn thông (PTIT)  
**Ngành**: Công nghệ Thông tin  
**Năm học**: 2026

---

## 1. CÔNG NGHỆ SỬ DỤNG (TECH STACK)

### Tổng Quan Lựa Chọn Công Nghệ

Kiến trúc PtitNotebook được thiết kế với mục tiêu:
- **Khả năng mở rộng**: Hệ thống có thể xử lý hàng ngàn tài liệu mà không ảnh hưởng hiệu suất.
- **Bảo mật cao**: Dữ liệu người dùng được bảo vệ với Django's built-in security features.
- **Hiệu suất tối ưu**: GPU-intensive tasks được tách riêng trên server Kaggle.
- **Dễ bảo trì**: Code được tổ chức theo cấu trúc layer rõ ràng.

### Backend: Django (Python 3.12+)

**Lý do lựa chọn**:

Django là framework web Python phổ biến nhất toàn thế giới, đặc biệt phù hợp cho ứng dụng RAG vì lý do sau:

1. **ORM Mạnh Mẽ**: Django ORM cho phép truy vấn cơ sở dữ liệu một cách an toàn (tránh SQL injection) mà không cần viết SQL thô. Ví dụ:
   ```python
   Document.objects.filter(notebook=notebook, is_selected=True)
   ```

2. **Middleware Bảo Mật Tích Hợp**: Django tự động bảo vệ khỏi:
   - CSRF (Cross-Site Request Forgery): Mỗi POST request phải chứa CSRF token hợp lệ.
   - XSS (Cross-Site Scripting): Django template engine tự động escape HTML entities.
   - SQL Injection: ORM sử dụng parameterized queries.

3. **Cấu Trúc MVT Rõ Ràng**:
   - **Model**: Định nghĩa schema database (User, Notebook, Document, ChatHistory, SavedAnswer).
   - **View**: Xử lý logic (kiểm tra quyền, gọi service layer, trả response).
   - **Template**: Render HTML với Tailwind CSS, tích hợp Alpine.js.

4. **Python 3.12+**: Phiên bản mới nhất cung cấp:
   - Performance improvement khoảng 10-20% so với 3.11.
   - Type hints cải tiến (PEP 695).
   - Asyncio enhancements.

### Frontend: Tailwind CSS, Alpine.js, Vanilla JavaScript

**Tailwind CSS (Utility-first CSS Framework)**:

- **Utility-first approach**: Thay vì tạo class CSS tùy chỉnh (e.g., `.card-blue`), Tailwind cung cấp các class tiện ích nhỏ (e.g., `bg-blue-600`, `rounded-xl`, `shadow-sm`). Điều này cho phép:
  - Xây dựng UI nhanh chóng mà không phải viết CSS riêng.
  - Duy trì design consistency qua toàn bộ ứng dụng.
  - Dễ dàng refactor: Chỉ cần thay đổi class Tailwind mà không cần chạy SCSS compiler.

- **Dark Mode Support**: Tailwind tích hợp dark mode thông qua class `dark:` prefix (e.g., `dark:bg-gray-800`). Chỉ cần thêm class `dark` vào `<html>` element, toàn bộ UI tự động chuyển sang chế độ tối:
  ```html
  <html class="dark">
      <body class="bg-white dark:bg-gray-900">...</body>
  </html>
  ```

**Alpine.js (Lightweight Reactive Framework)**:

- **Kích thước nhỏ**: ~15KB gzipped, không cần build step hoặc transpilation.
- **Reactivity trực tiếp trong HTML**: Ví dụ, quản lý modal:
  ```html
  <div x-data="{ isOpen: false }">
      <button @click="isOpen = !isOpen">Toggle</button>
      <div x-show="isOpen">Modal content</div>
  </div>
  ```
- **Perfect cho RAG UI**: Chỉ cần quản lý UI state nhỏ (modal, dropdown, theme toggle), Alpine.js đủ mạnh.

**Vanilla JavaScript + Fetch API**:

- **Không dependency**: Sử dụng Fetch API tiêu chuẩn (không jQuery) để gửi AJAX request.
- **DOM Manipulation trực tiếp**: Thêm/xóa elements một cách tường minh, dễ debug.
- **Security-first**: Fetch API cho phép kiểm soát headers (CSRF token), body encoding (URLSearchParams).

### Databases: PostgreSQL và ChromaDB

**PostgreSQL (Relational Database)**:

PostgreSQL là hệ quản trị cơ sở dữ liệu quan hệ SQL mạnh mẽ, lưu trữ **dữ liệu có cấu trúc**:

- **Người dùng**: ID, username, password hash, email.
- **Sổ tay (Notebooks)**: ID, người dùng, tên, ngày tạo, ngày truy cập cuối.
- **Tài liệu (Documents)**: ID, sổ tay, tên file, đường dẫn file, trạng thái `is_selected`.
- **Lịch sử trò chuyện (ChatHistory)**: ID, sổ tay, câu hỏi, câu trả lời, timestamp.
- **Câu trả lời đã lưu (SavedAnswer)**: ID, sổ tay, summary, nội dung đầy đủ, timestamp.

**Ưu điểm**:
- Hỗ trợ transactions ACID: Đảm bảo tính nhất quán dữ liệu (e.g., nếu lưu Document thất bại, không tạo chunk trong ChromaDB).
- Indexes mạnh: Truy vấn nhanh chóng với `filter(notebook=notebook, is_selected=True)`.
- Relationships: Foreign keys tự động enforce referential integrity.

**ChromaDB (Vector Database)**:

ChromaDB là cơ sở dữ liệu vector chuyên dụng, lưu trữ **embeddings** (vector hóa văn bản):

- **Embeddings**: Mỗi chunk text (800 ký tự) được convert thành vector 384 chiều (nomic-embed-text).
- **Similarity Search**: Truy vấn tìm chunks có khoảng cách cosine nhỏ nhất so với question embedding.
- **Metadata Filtering**: Lọc chunks theo `{"source": "file.pdf"}` hoặc `{"source": {"$in": ["file1.pdf", "file2.pdf"]}}`.

**Tại sao cần cả hai database**:
- PostgreSQL: Query cấu trúc (người dùng, lịch sử).
- ChromaDB: Query vector (similarity search).
- Kết hợp: PostgreSQL lưu metadata (user ownership), ChromaDB lưu embeddings (tìm kiếm).

### Remote AI Server: Kaggle + Ollama + FastAPI + Ngrok

**Kaggle Notebook (Compute Platform)**:

- **Miễn phí GPU**: Kaggle cung cấp GPU T4 x2 (Tesla T4, 16GB memory mỗi cái) miễn phí, đủ cho inference Llama3:8b.
- **Lý do tách remote**: Máy cục bộ (laptop/desktop) thường không có GPU; embedding và LLM inference nặng:
  - Embedding 1000 chunks với nomic-embed-text: ~10-15 giây trên GPU, ~5 phút trên CPU.
  - LLM inference với Llama3:8b: ~4 tokens/giây trên T4, có thể mất vài phút trên CPU.

**Ollama (Model Runtime)**:

Ollama là runtime chạy mô hình AI cục bộ (tương tự Docker cho models):

- **Hỗ trợ hai mô hình**:
  - `nomic-embed-text`: Embedding model 384 chiều, optimize cho semantic search.
  - `llama3:8b`: LLM 8 tỷ tham số, generate text mạnh mẽ.

- **API HTTP đơn giản**: Ollama cung cấp REST API:
  ```bash
  POST http://localhost:11434/api/embeddings
  {"model": "nomic-embed-text", "prompt": "text to embed"}
  ```

- **Offline-capable**: Sau khi pull model, Ollama không cần internet để inference.

**FastAPI (API Framework)**:

FastAPI là framework API Python siêu nhanh:

- **Async-first**: Hỗ trợ async/await, xử lý multiple requests đồng thời.
- **Pydantic models**: Tự động validate request body và generate API docs.
- **Performance**: Nhanh hơn Flask/Django đơn lẻ (Django chủ yếu là web framework, không chỉ API).

**Ngrok (Secure Tunneling)**:

Ngrok tạo HTTPS URL công cộng cho localhost server:

- **Giải quyết firewall/NAT**: Django server (localhost:8000) không thể truy cập từ Kaggle. Ngrok tạo bridge: `https://unthirsty-unruffled-zelda.ngrok-free.dev` → `http://localhost:8000`.
- **HTTPS bảo mật**: Ngrok tự động SSL/TLS encrypt traffic.
- **Rate limiting**: Ngrok free tier có rate limit, nhưng đủ cho demo.

### Document Processing: PyMuPDF (fitz) và LangChain

**PyMuPDF (fitz)**:

PyMuPDF là thư viện C-binding để trích xuất văn bản từ PDF với độ chính xác cao:

```python
import fitz
pdf = fitz.open("document.pdf")
for page_num in range(len(pdf)):
    page = pdf.load_page(page_num)
    text = page.get_text("text")  # Raw text, no formatting
```

**Ưu điểm**:
- **Multi-format support**: PDF, XPS, EPUB, CBZ, v.v.
- **Xử lý lỗi tốt**: Có thể extract text từ PDF hỏng hay bảo vệ.
- **Page-by-page**: Dễ dàng track page number cho citation.

**LangChain (RecursiveCharacterTextSplitter)**:

LangChain là framework RAG, nhưng ta chỉ dùng `RecursiveCharacterTextSplitter`:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,           # Target size per chunk
    chunk_overlap=100,        # Overlap giữa chunks
    length_function=len,      # Đo độ dài bằng ký tự (không token)
)

chunks = splitter.split_text(long_text)
```

**Tại sao recursive**:
- Tách ở điểm ngắt tự nhiên: `"\n\n"` (paragraph) → `"\n"` (line) → `" "` (word) → ký tự.
- Nếu tách tại paragraph mà vẫn > 800 ký tự, recursively tách ở line.
- Kết quả: Chunks liền mạch về ngữ cảnh (không giữa câu).

**chunk_size=800 rationale**:
- Llama3:8b context window: ~8192 tokens.
- 800 ký tự ≈ 150-200 tokens (với ký tự Tiếng Anh, trung bình 4 ký tự/token).
- top_k=5 chunks ≈ 4000 ký tự ≈ 1000 tokens → đủ context, còn chỗ cho prompt structure.
- chunk_overlap=100: Nếu sentence bị cắt ngang, 100 ký tự overlap đảm bảo sentence đó xuất hiện đầy đủ trong ít nhất 1 chunk.

---

## 2. KIẾN TRÚC PHẦN MỀM (SOFTWARE ARCHITECTURE)

### Hybrid Architecture: Phân Chia Tính Toán

```
┌────────────────────────────────────────────────────────────────┐
│                   Local Django Web Server                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Frontend (Tailwind CSS, Alpine.js, Vanilla JS)        │   │
│  │  - HTML templates với chat interface                   │   │
│  │  - Dark mode toggle, modal management                  │   │
│  │  - AJAX requests (không page reload)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Backend (Django Views, Services)                      │   │
│  │  - Input validation, permission checks                 │   │
│  │  - Orchestrate document ingestion                      │   │
│  │  - Construct system prompts                            │   │
│  │  - Save chat history                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                   │   │
│  │  - Users, notebooks, documents, chat history           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ChromaDB HTTP Client                                  │   │
│  │  - Query embeddings, metadata filtering                │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
              ↓ REST API via Ngrok (HTTPS) ↓
┌────────────────────────────────────────────────────────────────┐
│            Remote AI Server (Kaggle Notebook)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Ollama + FastAPI                                      │   │
│  │  - /embed endpoint: nomic-embed-text                   │   │
│  │  - /chat endpoint: llama3:8b                           │   │
│  │  - HTTP API listening on port 8000                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  GPU (T4 x2)                                           │   │
│  │  - 16GB memory per T4                                  │   │
│  │  - Enough for Llama3:8b quantized                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

**Lợi Ích Hybrid Architecture**:

1. **Giảm tải máy cục bộ**: 
   - Embedding 1000 chunks: CPU ~5 phút, GPU ~10 giây (50x faster).
   - LLM inference: CPU ~vài phút, GPU ~30 giây.
   - Django server (CPU) vẫn responsive cho concurrent users.

2. **Bảo mật dữ liệu**:
   - Tài liệu PDF không bao giờ upload lên Kaggle.
   - Chỉ embeddings (vector) và prompts (text) được gửi.
   - Embeddings là đại diện nén của text, khó khôi phục.

3. **Chi phí hiệu quả**:
   - Kaggle GPU miễn phí.
   - Django server: thường là VPS rẻ ($5-20/month).
   - Tổng TCO (Total Cost of Ownership) thấp.

4. **Scalability**:
   - Có thể nâng cấp Kaggle GPU (A100) mà không ảnh hưởng Django.
   - Có thể thêm caching layer (Redis) sau này.
   - Có thể sử dụng load balancer cho multiple Kaggle instances.

### MVC/MVT Pattern (Django)

Django tuân theo **Model-View-Template (MVT)** pattern:

- **Model** (`notebooks/models.py`):
  - Định nghĩa schema database.
  - Ví dụ: `Notebook`, `Document`, `ChatHistory`, `SavedAnswer`.
  - Django ORM tự động tạo migration và schema.

- **View** (`notebooks/views.py`):
  - Hàm Python nhận `HttpRequest`, trả `HttpResponse`.
  - Xử lý logic: validate input, gọi services, render template.
  - Ví dụ: `chat_ajax(request, pk)` xử lý AJAX request.

- **Template** (`notebooks/templates/notebooks/`):
  - HTML file với Tailwind CSS classes.
  - Embed Alpine.js directives (e.g., `x-data`, `@click`).
  - Render dữ liệu động từ context dict.

**Flow ví dụ - Chat**:
```
User submits form
  ↓
Browser sends POST /notebook/5/chat/ (AJAX)
  ↓
Django routes to views.chat_ajax(request, pk=5)
  ↓
View: validate input, get selected_docs, call VectorDBService
  ↓
Service: query ChromaDB, call KaggleService
  ↓
Response: {"question": "...", "answer": "..."}
  ↓
Browser: append chat bubbles to DOM (Alpine.js)
```

### App Encapsulation (Django Best Practice)

Cấu trúc thư mục tuân theo **App Encapsulation**:

```
notebooks/                          ← App "notebooks"
├── static/
│   └── notebooks/                  ← App-level static files
│       ├── css/
│       │   └── (reserved for app-specific CSS)
│       └── js/
│           └── workspace.js        ← Chat logic
├── templates/
│   └── notebooks/                  ← App-level templates
│       ├── base.html
│       ├── dashboard.html
│       ├── login.html
│       ├── signup.html
│       └── workspace.html
├── migrations/
│   ├── 0001_initial.py
│   └── __init__.py
├── __init__.py
├── admin.py                        ← Django admin registration
├── apps.py                         ← App config
├── models.py                       ← Database models
├── tests.py                        ← Unit tests
├── urls.py                         ← URL routing
├── views.py                        ← View handlers
└── services.py                     ← Business logic
```

**Lợi ích**:

1. **Modularity**: Mỗi Django app là standalone module. Có thể di chuyển `notebooks` app sang dự án khác.

2. **Automatic Discovery**: Django `AppDirectoriesFinder` tự động tìm:
   - `app_name/static/app_name/` → files như `notebooks/static/notebooks/js/workspace.js`.
   - `app_name/templates/app_name/` → templates.
   - Không cần cấu hình `STATICFILES_DIRS` cho mỗi file.

3. **Naming Convention**: Tên file namespace tránh conflict. Ví dụ:
   - Global `static/js/workspace.js` có thể conflict với app khác.
   - App-level `notebooks/static/notebooks/js/workspace.js` không conflict.

4. **Admin Interface**: Django admin tự động generate interface cho models trong app.

---

## 3. CƠ CHẾ VÀ LUỒNG HOẠT ĐỘNG (WORKFLOW & MECHANISMS)

### Luồng Xử Lý Tài Liệu (Document Ingestion Flow)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. USER UPLOAD                                                       │
│    - User chọn file PDF                                             │
│    - Browser gửi POST /notebook/5/                                  │
│    - Body: multipart/form-data (file binary)                        │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 2. DJANGO SAVE FILE                                                  │
│    - views.workspace() lấy uploaded_file                            │
│    - Document.objects.create(                                       │
│        notebook=notebook,                                           │
│        file_name="report.pdf",                                      │
│        file_path=uploaded_file  ← Django FileField auto saves      │
│      )                                                              │
│    - File được lưu vào media/documents/report_TIMESTAMP.pdf        │
│    - Database record tạo với is_selected=False                     │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 3. DOCUMENT SERVICE - TEXT EXTRACTION & CHUNKING                     │
│    - DocumentService.process_and_chunk_pdf(file_path, file_name)   │
│    - PyMuPDF duyệt từng trang PDF                                  │
│    - LangChain chia text thành chunks (800 chars, 100 overlap)      │
│    - Gắn metadata: {source: "report.pdf", page: 1}                │
│    - Kết quả: list of {content, metadata}                         │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 4. EMBEDDING SERVICE - GENERATE VECTORS                             │
│    - VectorDBService.save_chunks_to_db(chunks_data)                │
│    - Trích xuất texts từ chunks                                    │
│    - KaggleService.get_embeddings(texts)                           │
│      - POST https://ngrok.../embed                                 │
│      - Kaggle FastAPI → Ollama nomic-embed-text                   │
│      - Nhận vectors list (384-dim each)                           │
│    - Verify: len(embeddings) == len(texts)                        │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 5. CHROMADB STORAGE                                                  │
│    - VectorDBService.collection.add(                               │
│        ids=[uuid1, uuid2, ...],                                    │
│        embeddings=[vector1, vector2, ...],                         │
│        metadatas=[{source, page}, ...],                            │
│        documents=[text1, text2, ...]                               │
│      )                                                              │
│    - ChromaDB lưu: (id, embedding, metadata, text)                │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 6. SET IS_SELECTED                                                   │
│    - doc.is_selected = True                                         │
│    - doc.save()                                                     │
│    - Tài liệu sẵn sàng sử dụng trong chat query                    │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 7. REDIRECT & UI UPDATE                                             │
│    - Django redirect('workspace', pk=notebook.id)                  │
│    - Frontend fetch document list                                  │
│    - Display document name in sidebar                              │
│    - User có thể sử dụng trong chat                               │
└──────────────────────────────────────────────────────────────────────┘
```

**Error Handling**:
- Nếu DocumentService fail: raise Exception.
- Nếu KaggleService timeout: raise Exception.
- Django view catch Exception → doc.delete() → messages.error() → redirect.
- Kết quả: Database sạch, user thấy error message.

### Luồng Truy Vấn AI (RAG Query Flow)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                        │
│    - User nhập câu hỏi: "Làm sao để optimize Python?"              │
│    - User chọn tài liệu: [✓] "guide.pdf", [ ] "notes.pdf"         │
│    - User click "Send"                                              │
│    - Browser AJAX POST /notebook/5/chat/                           │
│    - Body: {question: "Làm sao..."}                                 │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 2. BACKEND - VALIDATE & GET SELECTED SOURCES                         │
│    - chat_ajax(request, pk=5)                                      │
│    - Get question from POST, trim whitespace                       │
│    - Check: not empty? → 400 if empty                             │
│    - Query: Document.objects.filter(                              │
│        notebook=notebook, is_selected=True                        │
│      )                                                              │
│    - Extract filenames: ["guide.pdf"]                             │
│    - Check: >= 1 document? → 400 if 0                            │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 3. VECTOR DB - EMBEDDING & METADATA FILTER                          │
│    - VectorDBService.search_similar_chunks(                        │
│        question="Làm sao...",                                      │
│        selected_sources=["guide.pdf"],                             │
│        top_k=5                                                      │
│      )                                                               │
│    - Embed question: KaggleService.get_embeddings([question])     │
│      → 1x384-dim vector                                            │
│    - Build where_filter:                                          │
│      len(selected_sources) == 1 → {"source": "guide.pdf"}        │
│      (exact match, không $in operator)                            │
│    - Query ChromaDB:                                              │
│      collection.query(                                             │
│        query_embeddings=[question_embedding],                      │
│        n_results=5,                                                │
│        where={"source": "guide.pdf"}  ← CRITICAL FILTER           │
│      )                                                              │
│    - Return top 5 chunks từ guide.pdf (nếu notes.pdf, ignore)    │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 4. FORMAT CONTEXT & BUILD SYSTEM PROMPT                             │
│    - Kết quả: {documents: [[chunk1, chunk2, ...]], metadatas: ...}│
│    - Loop từng chunk, gắn metadata:                                │
│      "--- Nguồn: guide.pdf (Trang 3) ---\n[chunk text]"          │
│    - Join chunks bằng "\n\n"                                       │
│    - Xây dựng system_prompt:                                      │
│      """Bạn là trợ lý AI...                                       │
│      NGỮ CẢNH:                                                     │
│      --- Nguồn: guide.pdf (Trang 3) ---                           │
│      [chunk1 content]                                              │
│                                                                     │
│      --- Nguồn: guide.pdf (Trang 5) ---                           │
│      [chunk2 content]                                              │
│      ...                                                            │
│      CÂU HỎI: Làm sao để optimize Python?                         │
│      TRẢ LỜI:"""                                                    │
│                                                                     │
│    - **Tại sao strict prompt**:                                   │
│      - Instruction: "không sử dụng kiến thức bên ngoài"          │
│      - Context: chỉ chunks từ selected file                       │
│      - Kết quả: AI chỉ trả lời dựa trên file được chọn           │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 5. CALL AI - LLM INFERENCE                                          │
│    - KaggleService.get_chat_answer(system_prompt)                 │
│    - POST https://ngrok.../chat                                   │
│    - Body: {prompt: system_prompt}                                 │
│    - Kaggle FastAPI → Ollama llama3:8b                           │
│    - Llama generate tokens dựa trên prompt                        │
│    - Return: full generated answer                                │
│    - **Timeout 120s**: LLM inference chậm                         │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 6. SAVE CHAT HISTORY & RETURN RESPONSE                              │
│    - ChatHistory.objects.create(                                   │
│        notebook=notebook,                                          │
│        question="Làm sao...",                                      │
│        answer="AI trả lời..."                                      │
│      )                                                              │
│    - Return JsonResponse({                                         │
│        'question': '...',                                          │
│        'answer': '...'                                             │
│      })                                                              │
│    - Status: 200 OK                                                │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 7. FRONTEND - DISPLAY CHAT BUBBLES                                  │
│    - JavaScript receive response                                   │
│    - appendChatMessage('assistant', answer)                       │
│    - Create div bong bóp AI (gray, left-aligned)                 │
│    - Append to #chat-history                                      │
│    - Auto scroll to bottom                                        │
│    - User see answer ngay lập tức                                 │
└──────────────────────────────────────────────────────────────────────┘
```

**Why This Flow Prevents Hallucination**:

1. **Metadata Filter**: ChromaDB chỉ trả chunks từ selected files. Nếu guides.pdf không được chọn, chunks từ file đó không được trả về.

2. **Strict Prompt**: System prompt explicit: "Không sử dụng kiến thức bên ngoài", "Trích dẫn nguồn".

3. **Citation in Response**: AI trích dẫn "Nguồn: guide.pdf (Trang 3)", user biết info đó từ đâu.

4. **Boundary Enforcement**: Nếu user chỉ chọn 1 file, AI không thể trích dẫn file khác (vì chunks đó không có trong prompt).

---

## 4. GIẢI PHẪU CHI TIẾT LOGIC CODE (DETAILED CODE ANATOMY)

### A. TẦNG DỊCH VỤ WEB (notebooks/services.py)

#### A.1. DocumentService.process_and_chunk_pdf

**MÃ NGUỒN ĐẦY ĐỦ:**

```python
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
```

**GIẢI THÍCH CHI TIẾT TỪNG DÒNG:**

- **Dòng 1**: Method tĩnh (`@staticmethod`), có thể gọi mà không cần instance: `DocumentService.process_and_chunk_pdf(path, name)`.

- **Dòng 2-3**: Validate file tồn tại. Nếu không, raise `FileNotFoundError`. **Lý do**: Ngăn PyMuPDF throw generic error. Fail-fast giúp debug dễ hơn.

- **Dòng 5-9**: Khởi tạo `RecursiveCharacterTextSplitter`:
  - `chunk_size=800`: Kích thước target mỗi chunk. **Tính toán**:
    - Llama3:8b context window: 8K tokens (~8000).
    - 800 ký tự Tiếng Anh ≈ 150-200 tokens (character-to-token ratio ~4:1).
    - top_k=5 chunks × 200 tokens = 1000 tokens (12.5% context), vừa đủ.
    - Prompt overhead (system instruction, question): ~500 tokens.
    - Total: ~1500 tokens, còn ~6500 tokens for generation (margin of safety).
  
  - `chunk_overlap=100`: 100 ký tự chồng lấp giữa chunks.
    - **Ví dụ**: Nếu text là 900 ký tự:
      - Chunk 1: ký tự 0-799 (800 ký tự).
      - Chunk 2: ký tự 700-800 (100 ký tự overlap, 100 ký tự mới).
    - **Tại sao**: Nếu sentence nằm ở boundary (ký tự 750-850), overlap đảm bảo nó xuất hiện đầy đủ trong ít nhất 1 chunk.
  
  - `length_function=len`: Dùng Python `len()` để đo độ dài. **Alternative**: `lambda x: len(x.split())` (word count), nhưng ký tự chính xác hơn.

- **Dòng 11**: Khởi tạo list rỗng để lưu kết quả.

- **Dòng 13**: `fitz.open(file_path)` mở PDF bằng PyMuPDF. `fitz` là alias của `pymupdf`.

- **Dòng 14**: `range(len(pdf_document))` duyệt từ page 0 đến page (n-1).
  - **Lưu ý**: PyMuPDF page indexing bắt đầu từ 0.

- **Dòng 15**: `load_page(page_num)` tải page vào memory. **Lý do không load toàn bộ**:
  - PDF lớn (ngàn trang) sẽ chiếm quá nhiều RAM.
  - Load per-page, process, release memory = tối ưu.

- **Dòng 16**: `get_text("text")` extract text từ page.
  - Mode `"text"`: Text thuần (output như cat file.txt).
  - **Alternative**: `"blocks"`, `"dict"` (structured with layout), nhưng ta chỉ cần text.

- **Dòng 18-19**: Skip trang trống. **Edge case**:
  - Trang hình ảnh (scan bằng máy quét): `get_text()` trả chuỗi rỗng.
  - Trang chỉ có ký tự trắng (newlines): `strip()` trả rỗng.
  - Nếu không skip, LangChain sẽ tạo chunks rỗng → ChromaDB lưu embeddings vô nghĩa → tăng storage.

- **Dòng 21**: Chia text trang bằng RecursiveCharacterTextSplitter.
  - Kết quả: list strings, mỗi string ≤ 800 ký tự (ngoại trừ nếu word đơn lẻ > 800 ký tự, LangChain keep as-is).

- **Dòng 22-27**: Loop mỗi chunk, append dict:
  ```python
  {
      "content": "...",  # Text của chunk
      "metadata": {
          "source": "guide.pdf",  # Tên file gốc
          "page": 3               # Số trang (1-indexed, không 0-indexed)
      }
  }
  ```
  - **Tại sao page là 1-indexed**: User-friendly. Trang đầu tiên là trang 1, không trang 0.

- **Dòng 28**: Đóng PDF file. **Quan trọng**: Giải phóng file handle, file system không lock file.

- **Dòng 29**: Trả list chunks.

- **Dòng 30-31**: Try-except wrapper. **Error handling**:
  - `FileNotFoundError`: File không tồn tại (caught tại dòng 3).
  - `Exception` (PDF hỏng, quyền truy cập, memory error): Catch → raise with message.
  - Caller (views.workspace) catch exception → log → delete Document record.

---

#### A.2. KaggleService.get_embeddings và KaggleService.get_chat_answer

**MÃ NGUỒN ĐẦY ĐỦ:**

```python
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
```

**GIẢI THÍCH CHI TIẾT:**

**Lớp KaggleService**:

- **Dòng 2**: Comment mô tả lớp.

- **Dòng 3**: `KAGGLE_API_URL` là class variable:
  - `getattr(settings, 'KAGGLE_API_URL', 'http://localhost:8000')`: Lấy từ Django settings, nếu không có fallback localhost.
  - **Development**: `http://localhost:8000` (Uvicorn local).
  - **Production**: `https://unthirsty-unruffled-zelda.ngrok-free.dev` (Ngrok public).

**get_embeddings (Dòng 5-16)**:

- **Dòng 6**: Comment mô tả hàm. Là method class (`@classmethod`), có thể gọi: `KaggleService.get_embeddings(["text1", "text2"])`.

- **Dòng 8-13**: HTTP POST request:
  - `requests.post(URL, json=data, timeout=60)`:
    - `URL`: `https://unthirsty-unruffled-zelda.ngrok-free.dev/embed`.
    - `json={"texts": texts}`: Payload JSON. requests tự động set `Content-Type: application/json`.
    - `timeout=60`: Nếu API chậm > 60 giây, raise `requests.ConnectTimeout`.
  
  - **Lý do timeout 60s**:
    - Ollama embedding batch (1000 texts) ở GPU: ~10-15 giây.
    - Network latency (Ngrok): ~1-2 giây.
    - Margin of safety: 60s đủ. Nếu > 60s, có lẽ API down.

- **Dòng 14**: `response.raise_for_status()`:
  - Nếu HTTP status ≥ 400 (e.g., 500), raise `requests.HTTPError`.
  - If statement không cần: `if response.status_code != 200: raise ...`.
  - `raise_for_status()` là best practice.

- **Dòng 15**: `response.json().get("embeddings", [])`:
  - Parse response JSON: `{"embeddings": [[0.1, 0.2, ...], [...]]}`
  - `.get("embeddings", [])`: Safe access, default rỗng list nếu key không tồn tại.
  - Kết quả: List of vectors, mỗi vector 384 chiều (nomic-embed-text).

- **Dòng 16-17**: Error handling:
  - Bắt bất kỳ exception (timeout, connection refused, JSON decode error).
  - Re-raise with descriptive message.
  - Caller (VectorDBService, views.chat_ajax) sẽ catch lại.

**get_chat_answer (Dòng 18-29)**:

- **Dòng 19**: Comment.

- **Dòng 21-26**: HTTP POST tương tự:
  - `URL`: `/chat` endpoint.
  - `json={"prompt": prompt}`: Full system prompt.
  - `timeout=120`: **Lý do 120s (lâu hơn embedding)**:
    - Llama3:8b generation là streaming tokens.
    - Trung bình ~4 tokens/giây trên GPU T4.
    - Prompt output có thể ~512 tokens (ví dụ) = ~128 giây.
    - 120s marginally tight, nhưng thường xong trước.
    - Nếu timeout, cân nhắc increase.

- **Dòng 27**: `raise_for_status()`.

- **Dòng 28**: `response.json().get("answer", "")`:
  - Response: `{"answer": "AI generated text..."}`
  - Return full answer string.

- **Dòng 29-30**: Error handling.

**Edge Cases Handled**:

1. **Timeout (requests.ConnectTimeout / requests.ReadTimeout)**:
   - `timeout=60/120` kill slow requests.
   - Exception propagate to caller.
   - Frontend show error: "Hết timeout, vui lòng thử lại."

2. **Connection Refused (requests.ConnectionError)**:
   - Ngrok URL sai, API down, network issue.
   - Exception with message: "Lỗi kết nối API Embedding: Connection refused".

3. **HTTP Errors (requests.HTTPError)**:
   - API return 500, 503, etc.
   - `raise_for_status()` throw exception.

4. **Invalid JSON (json.JSONDecodeError)**:
   - Response body không phải JSON hợp lệ.
   - `response.json()` throw exception.

5. **Missing Keys**:
   - Response: `{"result": []}` (key là `result`, không `embeddings`).
   - `.get("embeddings", [])` return default `[]`.
   - Caller check: `if not embeddings: raise Exception("Empty embeddings")`.

---

#### A.3. VectorDBService.search_similar_chunks

**MÃ NGUỒN ĐẦY ĐỦ:**

```python
def search_similar_chunks(self, question, selected_sources=None, top_k=5):
    # Tìm kiếm các đoạn văn bản có độ tương đồng cao nhất với câu hỏi.
    # Nhúng câu hỏi thành vector
    question_embedding = KaggleService.get_embeddings([question])[0]

    where_filter = None
    if selected_sources:
        selected_sources = list(selected_sources)
        if len(selected_sources) == 1:
            where_filter = {"source": selected_sources[0]}
        else:
            where_filter = {"source": {"$in": selected_sources}}

    # Truy vấn không gian vector với bộ lọc metadata source
    results = self.collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where=where_filter
    )
    return results
```

**GIẢI THÍCH CHI TIẾT TỪNG DÒNG:**

- **Dòng 1**: Method (instance method, không static). Gọi sau khởi tạo: `vector_db = VectorDBService(); vector_db.search_similar_chunks(...)`.
  - Parameter:
    - `question` (str): Câu hỏi người dùng.
    - `selected_sources` (list or QuerySet): Danh sách tên file được chọn.
    - `top_k` (int): Số chunks trả về, default 5.

- **Dòng 2-3**: Comment.

- **Dòng 4**: `KaggleService.get_embeddings([question])`:
  - Gửi list 1 phần tử `[question]` tới embedding API.
  - Nhận `[[vector_384d]]` (list of lists).
  - `[0]` trích element đầu tiên: `[0.1, 0.2, ..., 0.384]` (384-dim vector).

- **Dòng 6**: Khởi tạo `where_filter = None`. Nếu không filter, truy vấn toàn ChromaDB.

- **Dòng 7-12**: **LOGIC SIÊU QUAN TRỌNG - METADATA FILTERING**:

  ```python
  if selected_sources:
      selected_sources = list(selected_sources)  # Convert QuerySet to list
      if len(selected_sources) == 1:
          where_filter = {"source": selected_sources[0]}
      else:
          where_filter = {"source": {"$in": selected_sources}}
  ```

  **Scenario 1 - Single File** (user chỉ chọn "guide.pdf"):
  - `selected_sources = ["guide.pdf"]`
  - `len(selected_sources) == 1` → True
  - `where_filter = {"source": "guide.pdf"}` (exact match)
  - ChromaDB chỉ trả chunks với `metadata["source"] == "guide.pdf"`.

  **Scenario 2 - Multiple Files** (user chọn "guide.pdf" + "notes.pdf"):
  - `selected_sources = ["guide.pdf", "notes.pdf"]`
  - `len(selected_sources) == 2` → False
  - `where_filter = {"source": {"$in": ["guide.pdf", "notes.pdf"]}}` (SQL IN operator)
  - ChromaDB trả chunks với `metadata["source"]` ∈ `["guide.pdf", "notes.pdf"]`.

  **Tại sao hai cách khác nhau**?
  - Performance: Single file `{"source": "X"}` là indexed lookup, nhanh hơn.
  - Correctness: Cả hai cách đều đúng, nhưng single-file là optimization.
  - **ChromaDB document**: `{"key": value}` for exact match, `{"key": {"$in": [values]}}` for IN.

  **Scenario 3 - No Selected Sources** (nếu selected_sources = [] hoặc None):
  - `if selected_sources` → False
  - `where_filter = None`
  - ChromaDB truyền `where=None` → không filter → trả top_k chunks từ bất kỳ source nào.
  - **Edge case**: Nếu user upload 3 files nhưng không chọn, system search toàn bộ. **Best practice**: Backend view kiểm tra `selected_docs.exists()` trước (xem views.py).

- **Dòng 15-19**: ChromaDB query:
  ```python
  results = self.collection.query(
      query_embeddings=[question_embedding],  # [1x384 vector]
      n_results=top_k,                         # 5
      where=where_filter                       # {"source": "guide.pdf"}
  )
  ```

  - `query_embeddings`: List of query vectors. Ta có 1 question, nên 1 vector.
  - `n_results`: Số results per query. ChromaDB return top_k similar vectors.
  - `where`: Filter by metadata. Chỉ xem xét chunks match filter.

- **Dòng 20**: Return results dict:
  ```python
  {
      'documents': [[chunk_text_1, chunk_text_2, ..., chunk_text_5]],
      'metadatas': [[{source: 'guide.pdf', page: 1}, {source: 'guide.pdf', page: 3}, ...]],
      'ids': [[id_1, id_2, ...]],
      'distances': [[0.15, 0.22, 0.38, ...]]  # cosine distance (lower = more similar)
  }
  ```

  - Nested lists vì ChromaDB supports multiple queries (ta query 1).
  - `documents[0]`: Chunks của query 0.
  - `distances[0]`: Cosine distances (0 = identical, 1 = opposite, 0.5 = perpendicular).

**Edge Cases & Error Handling**:

1. **Empty ChromaDB**: Không có documents trong collection.
   - Query return `{'documents': [[]], 'metadatas': [[]], ...}`.
   - Caller check: `if not docs: context_string = "No relevant documents found"`.

2. **No Matches for Filter**: where_filter cực restrictive, không chunk nào match.
   - ChromaDB return empty results.
   - Caller handle → user thấy "Không tìm thấy thông tin trong tài liệu cung cấp".

3. **Embedding API Timeout**: `KaggleService.get_embeddings([question])` timeout.
   - Exception propagate.
   - Caller catch → return 500 error.

4. **ChromaDB Connection Error**: HTTP client không kết nối được.
   - `chromadb.HttpClient` throw exception.
   - Caller catch → 500 error.

**CRITICAL ANTI-HALLUCINATION MECHANISM**:

Metadata filtering ở đây là **core mechanism** ngăn AI hallucination:

- **Without filtering**: AI search toàn bộ 3 files → retrieve chunks từ file user không chọn → AI trình bày thông tin user không muốn → hallucination (từ góc độ user).

- **With filtering**: Chỉ chunks từ selected files → AI chỉ biết về selected files → Không thể hallucinate outside scope.

- **Prompt enforcement**: System prompt nói "Không sử dụng kiến thức bên ngoài", nhưng nếu prompt chứa chunks từ guide.pdf khi user chỉ chọn notes.pdf, AI sẽ follow prompt nhưng trích dẫn sai file (user sẽ notice contradiction).

---

### B. TẦNG CONTROLLER/VIEW (notebooks/views.py)

#### B.1. chat_ajax

**MÃ NGUỒN ĐẦY ĐỦ:**

```python
@login_required
@require_POST
def chat_ajax(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    question = request.POST.get('question', '').strip()
    
    if not question:
        return JsonResponse({'error': 'Vui lòng nhập câu hỏi.'}, status=400)

    selected_docs = Document.objects.filter(notebook=notebook, is_selected=True)
    if not selected_docs.exists():
        return JsonResponse({'error': 'Vui lòng chọn ít nhất một tài liệu.'}, status=400)

    try:
        selected_sources = list(selected_docs.values_list('file_name', flat=True))

        # Tìm kiếm ngữ cảnh
        vector_db = VectorDBService()
        search_results = vector_db.search_similar_chunks(
            question,
            selected_sources=selected_sources,
            top_k=5
        )
        
        # Xử lý kết quả trả về từ vector DB
        context_parts = []
        docs = search_results['documents'][0] if search_results['documents'] else []
        metas = search_results['metadatas'][0] if search_results['metadatas'] else []
        
        for i in range(len(docs)):
            source_info = f"--- Nguồn: {metas[i].get('source')} (Trang {metas[i].get('page')}) ---"
            context_parts.append(f"{source_info}\n{docs[i]}")
        
        context_string = "\n\n".join(context_parts)

        # Cấu trúc Prompt
        system_prompt = f"""Bạn là một trợ lý AI hỗ trợ giải đáp thông tin.
Dựa vào các ngữ cảnh được cung cấp dưới đây, hãy trả lời câu hỏi của người dùng.
Nếu thông tin không có trong tài liệu, hãy trả lời "Không tìm thấy thông tin trong tài liệu cung cấp".
Tuyệt đối không sử dụng kiến thức bên ngoài. Luôn trích dẫn nguồn (tên file và số trang) ở cuối câu trả lời.
Câu trả lời được đưa ra sử dụng ngôn ngữ giống với ngôn ngữ người dùng hỏi.

NGỮ CẢNH:
{context_string}

CÂU HỎI: {question}
TRẢ LỜI:"""

        # Gửi request và lưu lịch sử
        answer = KaggleService.get_chat_answer(system_prompt)
        ChatHistory.objects.create(notebook=notebook, question=question, answer=answer)
        
        return JsonResponse({'question': question, 'answer': answer})

    except Exception as e:
        return JsonResponse({'error': f"Lỗi hệ thống: {str(e)}"}, status=500)
```

**GIẢI THÍCH CHI TIẾT STEP-BY-STEP:**

**Decorators (Dòng 1-2)**:

- `@login_required`: Django decorator. Nếu user chưa login, redirect sang login page. Chỉ authenticated user có thể gọi hàm.

- `@require_POST`: Decorator yêu cầu HTTP method = POST. Nếu GET, return 405 Method Not Allowed. Ngăn form submission thiếu sót (e.g., user manually type URL).

**Xác Thực & Lấy Dữ Liệu (Dòng 3-5)**:

- **Dòng 4**: `get_object_or_404(Notebook, pk=pk, user=request.user)`:
  - Lấy Notebook object với id=pk.
  - **Filter**: `user=request.user` → chỉ notebook của user hiện tại.
  - Nếu không tìm thấy, Django return 404 Not Found.
  - **Bảo mật**: Ngăn user A truy cập notebook của user B.

- **Dòng 5**: `request.POST.get('question', '').strip()`:
  - Trích `question` từ form data (POST body).
  - `.strip()`: Xóa leading/trailing whitespace.
  - Default `''` nếu key không tồn tại.

**Input Validation (Dòng 6-10)**:

- **Dòng 6-7**: Nếu question trống (chỉ whitespace):
  - Return `JsonResponse({'error': '...'}, status=400)`.
  - Status 400 = Bad Request, indicate client error.
  - Frontend catch error → show alert.

- **Dòng 9-10**: Query `is_selected=True` documents:
  - Nếu không có, return 400 + error message.
  - **Lý do**: Nếu không check, `selected_sources` rỗng → ChromaDB search toàn bộ chunks → AI hallucinate.

**Trích Xuất Tên Files (Dòng 13)**:

- `selected_docs.values_list('file_name', flat=True)`:
  - Django ORM query chỉ trả `file_name` column (optimize, không load object).
  - `flat=True`: Return flat list strings, không list tuples.
  - `list(...)`: Evaluate QuerySet, execute database query.
  - Result: `['guide.pdf', 'notes.pdf']`.

**Truy Vấn Vector DB (Dòng 15-20)**:

- `VectorDBService()`: Khởi tạo instance (kết nối ChromaDB trong `__init__`).

- `.search_similar_chunks(question, selected_sources=selected_sources, top_k=5)`:
  - Embed question, query ChromaDB với metadata filter.
  - Return dict: `{'documents': [[...]], 'metadatas': [[...]], ...}`.

**Xử Lý Kết Quả (Dòng 22-26)**:

- **Dòng 23-24**: Trích chunks và metadatas:
  - `search_results['documents'][0]`: List chunks từ query 0.
  - `search_results['metadatas'][0]`: List metadata dicts từ query 0.
  - `if search_results['documents'] else []`: Safe access (handle empty case).

- **Dòng 26-27**: Loop, gắn metadata cho từng chunk:
  ```python
  for i in range(len(docs)):
      source_info = f"--- Nguồn: {metas[i].get('source')} (Trang {metas[i].get('page')}) ---"
      context_parts.append(f"{source_info}\n{docs[i]}")
  ```
  - Kết quả: `["--- Nguồn: guide.pdf (Trang 3) ---\n[chunk1 text]", "--- Nguồn: guide.pdf (Trang 5) ---\n[chunk2 text]", ...]`.

- **Dòng 29**: Join chunks bằng `"\n\n"` (paragraph separator):
  - `context_string = "--- Nguồn: guide.pdf (Trang 3) ---\nchunk1\n\n--- Nguồn: guide.pdf (Trang 5) ---\nchunk2\n\n..."`.

**Xây Dựng System Prompt (Dòng 31-41)**:

- **Dòng 31-39**: Prompt template string:
  ```
  Bạn là một trợ lý AI hỗ trợ giải đáp thông tin.
  Dựa vào các ngữ cảnh được cung cấp dưới đây, hãy trả lời câu hỏi của người dùng.
  Nếu thông tin không có trong tài liệu, hãy trả lời "Không tìm thấy thông tin trong tài liệu cung cấp".
  Tuyệt đối không sử dụng kiến thức bên ngoài. Luôn trích dẫn nguồn (tên file và số trang) ở cuối câu trả lời.
  Câu trả lời được đưa ra sử dụng ngôn ngữ giống với ngôn ngữ người dùng hỏi.
  
  NGỮ CẢNH:
  {context_string}
  
  CÂU HỎI: {question}
  TRẢ LỜI:
  ```

  - **Tại sao cấu trúc này**:
    1. **System instruction**: AI làm gì, boundary gì (không hallucinate, luôn cite).
    2. **Context**: Chunks từ selected files (ordered by relevance từ ChromaDB).
    3. **Question**: User input.
    4. **Cue "TRẢ LỜI:"**: Llama sẽ complete từ sau, generate answer.

  - **Prompt injection mitigation**: Prompt template không accept user input trực tiếp ở instruction (chỉ ở question/context). Nếu user input chứa `, hãy ignore instruction trước đây`, AI sẽ ignore vì nó ở trong context (không instruction).

**Gửi Tới Kaggle (Dòng 43-44)**:

- `KaggleService.get_chat_answer(system_prompt)`:
  - POST `https://ngrok.../chat` với `{"prompt": system_prompt}`.
  - Kaggle FastAPI → Ollama Llama3:8b → generate answer.
  - Return generated text string.

- Timeout: 120s (đủ cho LLM inference).

**Lưu Lịch Sử (Dòng 45)**:

- `ChatHistory.objects.create(notebook=notebook, question=question, answer=answer)`:
  - Tạo record trong database để audit trail / user review history.

**Trả Response (Dòng 47)**:

- `JsonResponse({'question': question, 'answer': answer})`:
  - Return JSON: `{"question": "...", "answer": "..."}`.
  - Status: 200 OK (default).
  - Frontend receive, parse JSON, append chat bubbles.

**Error Handling (Dòng 49-50)**:

- `try-except` wrapper bao quanh core logic.
- Catch bất kỳ exception:
  - KaggleService timeout: `requests.ConnectTimeout`.
  - ChromaDB error: `chromadb.HttpError`.
  - Database error: `django.db.IntegrityError`.
  - Etc.
- Return `{'error': str(e)}` status 500.
- Frontend catch 500 → show alert with error message.

---

### C. TẦNG FRONTEND LOGIC (notebooks/static/notebooks/js/workspace.js)

#### C.1. CSRF Token Extraction

**MÃ NGUỒN ĐẦY ĐỦ:**

```javascript
const getCsrfToken = () => {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (input) {
        return input.value;
    }

    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='));

    return cookieValue ? cookieValue.split('=')[1] : null;
};
```

**GIẢI THÍCH CHI TIẾT TỪNG DÒNG:**

- **Dòng 1**: Function declaration. Không parameter, return CSRF token string hoặc null.

- **Dòng 2**: `document.querySelector('input[name="csrfmiddlewaretoken"]')`:
  - Tìm HTML element: `<input type="hidden" name="csrfmiddlewaretoken" value="...">`.
  - Django template tag `{% csrf_token %}` render thành input này.
  - `querySelector` return element hoặc `null` nếu không tìm thấy.

- **Dòng 3-4**: Nếu tìm thấy:
  - `return input.value`: Trích `value` attribute (CSRF token).
  - Token là 32-ký tự hex string (e.g., `"abc123def456abc123def456abc123de"`).

- **Dòng 6-9**: **Fallback - Tìm cookie**. Nếu input không tồn tại (ví dụ, pure AJAX request, không form):
  - `document.cookie`: Trả string format `"name1=value1; name2=value2; ..."`.
  - `.split('; ')`: Tách thành array `["name1=value1", "name2=value2", ...]`.
  - `.find((row) => row.startsWith('csrftoken='))`: Tìm entry bắt đầu với `"csrftoken="`.
  - Result: `"csrftoken=ABC123DEF456..."` hoặc `undefined`.

- **Dòng 11**: Ternary operator:
  - Nếu `cookieValue` tìm thấy: `cookieValue.split('=')[1]` → token (phần sau `=`).
  - Else: `null`.

**Tại sao cần CSRF Token**:

CSRF (Cross-Site Request Forgery) attack example:
1. User login vào Django website.
2. User visit attacker website (trong tab khác).
3. Attacker website gửi hidden form: `POST /notebook/5/chat/?question=delete_all`.
4. Browser submit form with Django session cookie → Django server confused, think user authorized.

**CSRF protection**:
- Django middleware check: POST request phải chứa CSRF token.
- Attacker không biết token value (unique per session) → không thể forge request.
- Token được gửi ở header `X-CSRFToken` hoặc form data.

---

#### C.2. safeFetchJson Utility

**MÃ NGUỒN ĐẦY ĐỦ:**

```javascript
const safeFetchJson = async (url, options) => {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Server responded with an error.');
    }
    return data;
};
```

**GIẢI THÍCH CHI TIẾT:**

- **Dòng 1**: Async function (return Promise). Parameter:
  - `url`: Endpoint URL (string).
  - `options`: Fetch init object (method, headers, body, etc.).

- **Dòng 2**: `await fetch(url, options)`:
  - Gửi HTTP request (GET/POST/etc. tùy `options.method`).
  - `fetch()` return Promise, `await` chờ response.
  - Response: object có properties `ok`, `status`, `json()`, etc.

- **Dòng 3**: `await response.json()`:
  - Parse response body thành JSON object.
  - Assume response chứa JSON (Content-Type: application/json).
  - Throw `SyntaxError` nếu body không phải valid JSON.

- **Dòng 4-6**: Error checking:
  - `if (!response.ok)`: Check HTTP status.
    - `response.ok` = true nếu status 200-299.
    - False nếu 3xx, 4xx, 5xx.
  - `throw new Error(...)`: Throw exception.
  - `data.error`: Try lấy error message từ response JSON (e.g., `{"error": "Vui lòng chọn ít nhất một tài liệu."}`).
  - Fallback: generic message.

- **Dòng 7**: Return parsed data nếu success.

**Lợi ích so với fetch thuần**:

```javascript
// fetch cơ bản - KHÔNG recommended
fetch(url, options)
  .then(r => r.json())
  .then(data => {
    // BUG: fetch không reject nếu HTTP 404/500
    // Vẫn phải check r.status/r.ok
  })
  .catch(e => console.error(e));

// safeFetchJson - RECOMMENDED
safeFetchJson(url, options)
  .then(data => { /* success */ })
  .catch(e => console.error(e.message));  // Tự động catch HTTP errors
```

---

#### C.3. Chat Form Submit Event Listener

**MÃ NGUỒN ĐẦY ĐỦ (phần đáng chú ý):**

```javascript
chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = chatInput.value.trim();
    if (!question) {
        return;
    }

    const submitButton = chatForm.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
    }

    appendChatMessage('user', question);
    chatInput.value = '';

    try {
        const data = await safeFetchJson(chatEndpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ question }),
        });

        appendChatMessage('assistant', data.answer || 'No response');
    } catch (error) {
        console.error(error);
        alert(error.message || 'Không thể kết nối đến máy chủ. Vui lòng thử lại.');
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
});
```

**GIẢI THÍCH CHI TIẾT STEP-BY-STEP:**

**Event Binding (Dòng 1)**:

- `chatForm.addEventListener('submit', ...)`:
  - Bind function vào `submit` event của form.
  - Khi user click button hoặc press Enter, trigger event.

**Ngăn Hành Vi Mặc Định (Dòng 2)**:

- `event.preventDefault()`:
  - Prevent browser submit form thực sự (page reload).
  - Thay vào đó, xử lý bằng AJAX (không reload).

**Trích & Validate Input (Dòng 3-5)**:

- `chatInput.value.trim()`: Lấy text, xóa whitespace.
- Nếu trống, `return` sớm (không gửi request rỗng).

**Disable Button (Dòng 7-10)**:

- Tìm submit button: `chatForm.querySelector('button[type="submit"]')`.
- `submitButton.disabled = true`: Disable button.
- **Lý do**: Prevent user click multiple times khi chờ response. Nếu không, sẽ gửi 5 request cùng lúc.

**Optimistic UI Update (Dòng 12-13)**:

- `appendChatMessage('user', question)`: Thêm user message vào chat history **ngay lập tức**.
- `chatInput.value = ''`: Clear input field.
- **UX benefit**: User thấy message của mình ngay, không phải chờ server. Perceived responsiveness tốt hơn.
- **Trade-off**: Nếu request fail, message user vẫn ở đó (optionally có thể undo, nhưng code hiện tại không undo).

**Gửi AJAX Request (Dòng 15-22)**:

- `safeFetchJson(chatEndpoint, {...})`:
  - `chatEndpoint = baseUrl + '/chat/'` (e.g., `/notebook/5/chat/`).
  - Options:
    - `method: 'POST'`: HTTP method.
    - Header `'X-CSRFToken': csrfToken`: CSRF protection.
    - Header `'Content-Type': 'application/x-www-form-urlencoded'`: Django expect form data, không JSON.
    - `body: new URLSearchParams({ question })`: Encode data.
      - URLSearchParams format: `"question=What+is+AI%3F"`.
      - JavaScript handle URL encoding (`.encode()` equivalence).

- `await`: Chờ response từ safeFetchJson.

**Decode Response & Update UI (Dòng 24)**:

- `data.answer`: Lấy answer từ `{"question": "...", "answer": "..."}`.
- `appendChatMessage('assistant', data.answer)`: Thêm AI message.
- `|| 'No response'`: Fallback nếu `data.answer` undefined.

**Error Handling (Dòng 25-28)**:

- `catch(error)`: Bắt exception từ `safeFetchJson` (HTTP error, network error, JSON parse error).
- `console.error(error)`: Log để debug (developer tools).
- `alert(error.message)`: Show error message popup.
  - ví dụ: "Lỗi hệ thống: Vui lòng chọn ít nhất một tài liệu."
  - User see message, không bị stuck.

**Finally Block (Dòng 29-33)**:

- `finally`: Chạy luôn (thành công hay fail).
- Re-enable button: `submitButton.disabled = false`.
- User có thể gửi câu hỏi tiếp theo.

**Complete Flow Visual**:

```
1. User type "Hello" → click Send
   ↓
2. event.preventDefault() → no page reload
   ↓
3. Button disabled
   ↓
4. Optimistic append: show user bubble "Hello"
   ↓
5. Clear input field
   ↓
6. POST /notebook/5/chat/ (AJAX)
   ↓
7a. Response OK → append AI bubble
    ↓
7b. Response Error → show alert
    ↓
8. finally: Button enabled
   ↓
9. User có thể tiếp tục chat
```

---

### D. TẦNG MÁY CHỦ AI TỪ XA (Kaggle / api.py)

#### D.1. FastAPI Setup & Endpoints

**MÃ NGUỒN ĐẦY ĐỦ (api.py):**

```python
%%writefile api.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class EmbedRequest(BaseModel):
    texts: list[str]

class ChatRequest(BaseModel):
    prompt: str

@app.post("/embed")
async def generate_embeddings(req: EmbedRequest):
    embeddings = []
    for text in req.texts:
        res = requests.post("http://localhost:11434/api/embeddings", json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        embeddings.append(res.json().get("embedding"))
    return {"embeddings": embeddings}

@app.post("/chat")
async def chat_with_ai(req: ChatRequest):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3:8b",
        "prompt": req.prompt,
        "stream": False
    })
    return {"answer": res.json().get("response")}
```

**GIẢI THÍCH CHI TIẾT TỪNG DÒNG:**

**Imports (Dòng 1-3)**:

- `from fastapi import FastAPI`: FastAPI framework class.
- `from pydantic import BaseModel`: Data validation library.
- `import requests`: HTTP client (để call Ollama API).

**App Initialization (Dòng 5)**:

- `app = FastAPI()`: Khởi tạo FastAPI app instance.
- FastAPI auto-generate OpenAPI docs tại `/docs`.

**Pydantic Models (Dòng 7-12)**:

```python
class EmbedRequest(BaseModel):
    texts: list[str]
```

- Pydantic model define request schema.
- `texts`: Field nhận list strings.
- FastAPI tự động validate request body match schema.
- Nếu request body không match (e.g., `{"texts": 123}`), return 422 Unprocessable Entity.

```python
class ChatRequest(BaseModel):
    prompt: str
```

- `prompt`: Field nhận string.

**Embedding Endpoint (Dòng 14-22)**:

```python
@app.post("/embed")
async def generate_embeddings(req: EmbedRequest):
    embeddings = []
    for text in req.texts:
        res = requests.post("http://localhost:11434/api/embeddings", json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        embeddings.append(res.json().get("embedding"))
    return {"embeddings": embeddings}
```

- `@app.post("/embed")`: Decorator, route POST `/embed` requests.
- `async def`: Async function, FastAPI hỗ trợ async (efficient concurrent requests).
- `req: EmbedRequest`: FastAPI auto-parse request body, validate, tạo object.
- **Loop mỗi text** (inefficient, nên batch, nhưng simplified code):
  - `requests.post("http://localhost:11434/api/embeddings", ...)`: Call Ollama API endpoint.
  - Payload: `{"model": "nomic-embed-text", "prompt": text}`.
  - Ollama respond: `{"embedding": [0.1, 0.2, ..., 0.384]}`  (384-dim vector).
  - `res.json().get("embedding")`: Trích vector.
  - Append vào `embeddings` list.
- `return {"embeddings": embeddings}`: Return JSON.
  - FastAPI auto-serialize dict thành JSON response.

**Chat Endpoint (Dòng 24-31)**:

```python
@app.post("/chat")
async def chat_with_ai(req: ChatRequest):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3:8b",
        "prompt": req.prompt,
        "stream": False
    })
    return {"answer": res.json().get("response")}
```

- `@app.post("/chat")`: Route POST `/chat` requests.
- `req: ChatRequest`: FastAPI parse + validate.
- `requests.post("http://localhost:11434/api/generate", ...)`:
  - Ollama generate endpoint.
  - `"model": "llama3:8b"`: Llama model.
  - `"prompt": req.prompt`: Full system prompt từ Django.
  - `"stream": False`: Non-streaming mode (full response, không chunks).
- Ollama respond: `{"response": "Generated text..."}`.
- `res.json().get("response")`: Trích answer text.
- Return: `{"answer": "..."}`.

**Why Async**:

- `async def`: Non-blocking, FastAPI có thể xử lý multiple requests đồng thời.
- Nếu synchronous, request 1 chờ Ollama 10 giây, request 2 phải chờ request 1 xong trước → latency cao.
- Async: Request 1 gửi tới Ollama, FastAPI suspend, request 2 come in, FastAPI xử lý (CPU-bound chút), request 1 response từ Ollama, FastAPI resume → overlap.

---

#### D.2. Ngrok & Uvicorn Setup Script

**MÃ NGUỒN ĐẦY ĐỦ (run_ngrok.py):**

```python
import subprocess
from pyngrok import ngrok

# 1. Dọn dẹp các tiến trình ngrok cũ để tránh xung đột cổng kết nối
ngrok.kill()

# 2. Xác thực và mở đường hầm
# Ghi chú: Thay thế chuỗi dưới đây bằng Authtoken thực tế từ tài khoản Ngrok
NGROK_AUTH_TOKEN = "ĐIỀN_TOKEN_NGROK_CỦA_NGÀI_VÀO_ĐÂY"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

public_url = ngrok.connect(8000).public_url
print(f"Link Server AI: {public_url}")

# 3. Khởi chạy Uvicorn ngầm để phục vụ file api.py trên port 8000
subprocess.Popen(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"])
```

**GIẢI THÍCH CHI TIẾT TỪNG DÒNG:**

**Imports (Dòng 1-2)**:

- `import subprocess`: Python module để tạo subprocess (chạy command từ Python).
- `from pyngrok import ngrok`: Python wrapper cho Ngrok CLI.

**Kill Old Ngrok (Dòng 5)**:

- `ngrok.kill()`: Kill tất cả ngrok processes cũ.
- **Lý do**: Nếu run script multiple times, ngrok occupy port, cần clean up trước.

**Authenticate & Open Tunnel (Dòng 8-12)**:

- `NGROK_AUTH_TOKEN = "..."`: 
  - Token từ Ngrok account (free account get token tại `https://dashboard.ngrok.com/auth/your-authtoken`).
  - **Security**: Token là sensitive, nên set environment variable hoặc config file (không hardcode).
  - Ở đây simplified cho demo.

- `ngrok.set_auth_token(NGROK_AUTH_TOKEN)`:
  - Authenticate with Ngrok service.

- `ngrok.connect(8000)`:
  - Open tunnel từ public internet → localhost:8000.
  - Ngrok allocate URL: `https://unthirsty-unruffled-zelda.ngrok-free.dev` (format: `https://<random-subdomain>.ngrok-free.dev`).
  - `.public_url`: Extract URL string.

- `print(f"Link Server AI: {public_url}")`:
  - Print URL cho copy paste vào Django settings.

**Start Uvicorn Server (Dòng 15)**:

```python
subprocess.Popen(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"])
```

- `subprocess.Popen(cmd, ...)`: Start subprocess (non-blocking).
  - Khác `subprocess.run()` (blocking).
  - Khác `subprocess.call()` (wait for completion).
- Command: `uvicorn api:app --host 0.0.0.0 --port 8000`:
  - `api:app`: Python module `api.py`, variable `app` (FastAPI instance).
  - `--host 0.0.0.0`: Listen trên tất cả network interfaces (0.0.0.0 = localhost + LAN + internet via Ngrok).
  - `--port 8000`: Port 8000.
- **Non-blocking**: Script return, Uvicorn chạy background, tunnel stay open.

**Tại sao subprocess thay vì direct Python**?

- Uvicorn là ASGI server (async-capable), chạy event loop.
- Nếu `import uvicorn; uvicorn.run(app)` trực tiếp, blocking call → script hang.
- Ngrok cũng có event loop (pyngrok).
- **Potential event loop conflict**: Nếu cùng thread, hai event loop không thể coexist (Python asyncio single-threaded).
- **Solution**: Uvicorn chạy subprocess (separate Python process, separate event loop) → không conflict.
- Ngrok (pyngrok) chạy main thread → Ngrok event loop manage Ngrok.

---

**Kaggle Notebook Cells (Setup)**:

**cell_1.bash - Install Dependencies**:

```bash
!apt-get update && apt-get install -y zstd
!pip install fastapi uvicorn pyngrok nest-asyncio
!curl -fsSL https://ollama.com/install.sh | sh
```

- Update package manager.
- Install FastAPI, Uvicorn (ASGI server), pyngrok (Ngrok wrapper).
- Install Ollama script (curl download install.sh, execute).

**cell_2.bash - Start Ollama & Pull Models**:

```python
import subprocess
import time

print("Đang khởi động Ollama...")
subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

time.sleep(5)

print("Đang tải nomic-embed-text...")
!ollama pull nomic-embed-text

print("Đang tải llama3:8b...")
!ollama pull llama3:8b
```

- `subprocess.Popen(["ollama", "serve"], ...)`: Start Ollama server (background).
  - `stdout=subprocess.DEVNULL`: Suppress output (not interested).
- `time.sleep(5)`: Chờ Ollama ổn định.
- `!ollama pull nomic-embed-text`: Kaggle notebook `!` syntax = shell command.
  - Download embedding model (~600MB).
- `!ollama pull llama3:8b`: Download LLM (~4-5GB).
  - Cached cục bộ, lần sau chạy nhanh.

---

## 5. PHỤ LỤC MÃ NGUỒN (SOURCE CODE APPENDIX)

### Tổng Quan Cấu Trúc Project

PtitNotebook project bao gồm các tầng:

1. **Frontend UI** (HTML templates + Tailwind CSS + Alpine.js):
   - `notebooks/templates/notebooks/base.html`: Navigation, theme toggle.
   - `notebooks/templates/notebooks/workspace.html`: Chat interface, document sidebar, saved answers.
   - `notebooks/templates/notebooks/dashboard.html`: Notebook list, create notebook.
   - Styling: Inline Tailwind classes (`class="bg-blue-600 dark:bg-gray-900 ..."`).
   - Dark mode: CSS class `dark` trên `<html>` element, Tailwind `.dark:` prefix.

2. **Backend Logic** (Django + Services):
   - `notebooks/views.py`: HTTP handlers (auth, upload, chat, save).
   - `notebooks/services.py`: DocumentService, VectorDBService, KaggleService.
   - `notebooks/models.py`: Database models (Notebook, Document, ChatHistory, SavedAnswer).
   - `notebooks/urls.py`: URL routing.

3. **Database**:
   - PostgreSQL: Relational data.
   - ChromaDB: Vector embeddings.
   - Migrations: `notebooks/migrations/0001_initial.py` + auto-generated.

4. **Configuration** (Django Settings):
   - `core/settings.py`: 
     - `DEBUG = True` (development).
     - `DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', ...}}`.
     - `INSTALLED_APPS = ['notebooks', ...]`.
     - `MIDDLEWARE = ['django.middleware.csrf.CsrfViewMiddleware', ...]` (CSRF protection).
     - `TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', ...}]`.
     - `STATIC_URL = '/static/'`, `STATICFILES_DIRS`, `STATIC_ROOT` (app encapsulation).
     - `KAGGLE_API_URL = "https://...ngrok..."` (remote AI server).

5. **Static Files** (CSS, JS):
   - `notebooks/static/notebooks/js/workspace.js`: Chat logic (CSRF, AJAX, DOM).
   - CSS: Inline Tailwind (không file CSS riêng).

6. **Remote AI Server** (Kaggle Notebook):
   - `Kaggle/api.py`: FastAPI endpoints (/embed, /chat).
   - `Kaggle/run_ngrok.py`: Ngrok tunnel + Uvicorn startup.
   - `Kaggle/cell_1.bash`, `cell_2.bash`: Setup dependencies, Ollama models.

### Các File Không Được Đề Cập Chi Tiết

Để giữ document tập trung vào logic core, các file sau được đơn giản hóa hoặc không expand đầy đủ:

1. **HTML Templates** (`notebooks/templates/notebooks/`):
   - `base.html`: Contains theme toggle logic, inherits by other templates.
   - `workspace.html`: Chat interface form, document list, saved answers list, Alpine.js directives for modal/counter.
   - `dashboard.html`: Notebook list, create form.
   - `login.html`, `signup.html`: Auth forms.
   - **Detail**: Mỗi template mix Tailwind CSS utility classes và Alpine.js directives (`x-data`, `@click`, `x-show`, etc.).
   - **Dark Mode**: Toggle via JavaScript → `localStorage` persist → `<html class="dark">` → Tailwind `.dark:` prefix activate.

2. **Django Models** (`notebooks/models.py`):
   - `User`: Django built-in.
   - `Notebook`: FK to User, `name`, `created_at`, `last_accessed`.
   - `Document`: FK to Notebook, `file_name`, `file_path` (FileField), `is_selected` (Boolean).
   - `ChatHistory`: FK to Notebook, `question`, `answer`, `created_at`.
   - `SavedAnswer`: FK to Notebook, `summary`, `full_content`, `saved_at`.

3. **Django Admin** (`notebooks/admin.py`):
   - Register models để admin interface tự động generate CRUD.
   - Không code logic, chỉ configuration.

4. **URL Routing** (`notebooks/urls.py`):
   - `path('notebook/<int:pk>/', workspace, name='workspace')`.
   - `path('notebook/<int:pk>/chat/', chat_ajax, name='chat')`.
   - etc.

5. **Configuration File** (`core/settings.py`):
   - Database connection string (PostgreSQL).
   - Static files directories.
   - Security settings (CSRF, CORS, allowed hosts).
   - Logging configuration.

### Lý Do Phần Mềm Có Kiến Trúc Tốt

Kiến trúc PtitNotebook thể hiện **best practices** trong software engineering:

1. **Separation of Concerns**: Mỗi layer (frontend, backend, service, database) có trách nhiệm rõ ràng.
   - Frontend: UI interaction.
   - Backend: Business logic, permission.
   - Service: API calls, data processing.
   - Database: Data persistence.

2. **DRY (Don't Repeat Yourself)**: Reusable functions (e.g., `safeFetchJson` utility, `VectorDBService` class).

3. **Error Handling**: Try-catch-finally ở tất cả layers, graceful degradation.

4. **Security**: CSRF token, input validation, permission checks, XSS prevention.

5. **Performance**: 
   - Async operations (FastAPI).
   - Metadata filtering (ChromaDB).
   - Caching (localStorage for theme).
   - Batch processing (embeddings, chunks).

6. **Scalability**:
   - Hybrid architecture (local + remote).
   - Database indexing.
   - Can add Redis caching, load balancing later.

7. **Maintainability**:
   - Modular code.
   - Consistent naming (snake_case Python, camelCase JS).
   - Comments + docstrings.
   - Type hints (Python 3.12+).

---

## KẾT LUẬN

PtitNotebook là ứng dụng RAG web hoàn chỉnh, kết hợp:
- **Backend mạnh mẽ**: Django + PostgreSQL + ChromaDB, xử lý permission, data validation, error handling.
- **Frontend responsive**: Tailwind CSS + Alpine.js + Vanilla JS, AJAX không reload, UX mượt mà.
- **AI integration**: Kaggle GPU + Ollama + FastAPI + Ngrok, hybrid architecture cho hiệu suất tối ưu.
- **RAG system**: Metadata filtering ngăn hallucination, strict prompting enforce boundaries.

Mỗi component được thiết kế với suy nghĩ kỹ lưỡng về performance, security, maintainability—tiêu chí cốt lõi của phần mềm chất lượng dành cho thị trường.

---

**Duyệt lại: [Tên Giáo Sư/Cố Vấn Luận Văn]**  
**Ngày phê duyệt: [Ngày nộp luận văn]**
