# Hướng dẫn Cài đặt PtitNotebook

## 1. Giới thiệu Tổng quan

**PtitNotebook** là một ứng dụng web thông minh cho phép người dùng tải lên các tài liệu (PDF, TXT), tương tác với một chatbot AI, và lưu trữ các câu trả lời quan trọng. 

### Kiến trúc Hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                     Local Web Application                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Frontend (Tailwind CSS, Alpine.js, HTML)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↑ ↓ (Fetch API)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Backend (Django, Python 3.12+)                     │  │
│  │   - Authentication & Authorization                  │  │
│  │   - Document Management                             │  │
│  │   - Chat History Tracking                           │  │
│  │   - Saved Answers Storage                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↑ ↓ (HTTP/REST)                    │
│  ┌──────────────────┐  ┌──────────────────────────────┐    │
│  │   PostgreSQL     │  │   ChromaDB (Vector DB)       │    │
│  │  (Relational)    │  │  (Document Embeddings)       │    │
│  └──────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           ↓ ↑ (HTTP - Ngrok Tunnel)
┌─────────────────────────────────────────────────────────────┐
│              Remote Kaggle AI Server (GPU T4 x2)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                 │  │
│  │  - POST /embed: Text → Vector Embeddings             │  │
│  │  - POST /chat: Question + Context → AI Response      │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ ↑                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Ollama (Local LLM Engine)                           │  │
│  │  - llama3:8b (Model cho chat)                       │  │
│  │  - nomic-embed-text (Model cho embeddings)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Ngrok Tunnel: Exposes FastAPI to public internet           │
└─────────────────────────────────────────────────────────────┘
```

### Công nghệ Chính

| Thành phần | Công nghệ |
|-----------|-----------|
| Backend | Django 4.2+, Python 3.12+ |
| Frontend | Tailwind CSS, Alpine.js, Fetch API |
| Cơ sở dữ liệu (Quan hệ) | PostgreSQL 12+ |
| Cơ sở dữ liệu (Vector) | ChromaDB |
| AI Server | Kaggle Notebook, Ollama, FastAPI, Ngrok |
| Container | Docker, Docker Compose |

---

## 2. Hướng dẫn Cài đặt Local Web App

Chọn **một trong ba phương án** phù hợp với hệ điều hành và công cụ của mình.

### Phương án 1: Linux / WSL + Docker Compose

**Yêu cầu Tiên quyết:**
- Python 3.12 hoặc cao hơn
- Docker & Docker Compose đã cài đặt
- Git để clone repository

**Các Bước Thực hiện:**

#### 1.1 Clone Repository
```bash
git clone <repository-url>
cd ptitnotebook
```

#### 1.2 Tạo Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate
```

#### 1.3 Khởi chạy PostgreSQL và ChromaDB với Docker Compose
```bash
docker-compose up -d
```

**Kiểm tra trạng thái:**
```bash
docker-compose ps
```

Bạn sẽ thấy hai container:
- `postgres` (cổng 5432)
- `chroma` (cổng 8000)

#### 1.4 Các bước tiếp theo: Xem mục **3. Khởi chạy Django**

---

### Phương án 2: Windows + Docker Desktop

**Yêu cầu Tiên quyết:**
- Python 3.12 hoặc cao hơn
- Docker Desktop enabled (với WSL2 backend)
- Git Bash hoặc PowerShell

**Các Bước Thực hiện:**

#### 2.1 Clone Repository
```bash
git clone <repository-url>
cd ptitnotebook
```

#### 2.2 Tạo Virtual Environment

Nếu dùng **PowerShell**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Nếu dùng **Git Bash hoặc cmd**:
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 2.3 Khởi chạy PostgreSQL và ChromaDB với Docker Compose

Đảm bảo Docker Desktop đang chạy, sau đó:
```bash
docker-compose up -d
```

**Kiểm tra trạng thái:**
```bash
docker-compose ps
```

#### 2.4 Các bước tiếp theo: Xem mục **3. Khởi chạy Django**

---

### Phương án 3: Windows KHÔNG có Docker

**Lưu ý:** Phương án này yêu cầu cài đặt PostgreSQL trực tiếp trên máy Windows.

**Yêu cầu Tiên quyết:**
- Python 3.12 hoặc cao hơn
- PostgreSQL 12+ (cài đặt locally)
- Git

**Các Bước Thực hiện:**

#### 3.1 Clone Repository
```bash
git clone <repository-url>
cd ptitnotebook
```

#### 3.2 Tạo Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 3.3 Cài đặt PostgreSQL Locally

- Tải PostgreSQL từ: https://www.postgresql.org/download/windows/
- Chạy installer và ghi nhớ mật khẩu superuser (postgres)
- Đặt default port là `5432`
- Sau khi cài đặt, mở **pgAdmin 4** hoặc **psql** command line

**Tạo Database mới:**
```sql
CREATE DATABASE ptitnotebook;
```

#### 3.4 Cập nhật Django Settings

Mở file `core/settings.py` và tìm phần `DATABASES`. Đảm bảo cấu hình như sau:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ptitnotebook',
        'USER': 'postgres',
        'PASSWORD': '<your-postgres-password>',  # Thay bằng mật khẩu bạn đã đặt
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 3.5 ChromaDB Chạy Local (Không cần Docker)

ChromaDB sẽ chạy ở chế độ persistent local:

```python
# Trong core/settings.py, thêm:
CHROMA_DB_PATH = os.path.join(BASE_DIR, 'chroma_db')
```

Hoặc bỏ qua nếu bạn chỉ muốn sử dụng in-memory ChromaDB cho development.

#### 3.6 Các bước tiếp theo: Xem mục **3. Khởi chạy Django**

---

## 3. Khởi chạy Django (Chung cho cả 3 Phương án)

Sau khi hoàn thành cài đặt cơ sở dữ liệu, thực hiện các bước sau:

### 3.1 Cài đặt Dependencies

Đảm bảo virtual environment đã được kích hoạt:

```bash
pip install -r requirements.txt
```

**Dự kiến thời gian:** 3-5 phút (tùy vào tốc độ mạng)

### 3.2 Chạy Migrations

```bash
python manage.py migrate
```

Lệnh này sẽ:
- Tạo các bảng trong PostgreSQL (User, Notebook, Document, ChatHistory, SavedAnswer)
- Khởi tạo schema cơ sở dữ liệu

### 3.3 Tạo Superuser (Admin)

```bash
python manage.py createsuperuser
```

Bạn sẽ được hỏi:
- **Username:** (gõ tên đăng nhập, ví dụ: `admin`)
- **Email:** (gõ email của bạn)
- **Password:** (gõ mật khẩu mạnh)
- **Password (again):** (gõ lại mật khẩu)

### 3.4 Khởi động Server Django

```bash
python manage.py runserver 8080
```

**Output mong đợi:**
```
Starting development server at http://127.0.0.1:8080/
Quit the server with CONTROL-C.
```

Truy cập vào: **http://localhost:8080**

### 3.5 Truy cập Admin Panel

- URL: `http://localhost:8080/admin`
- Username/Password: Những thông tin bạn vừa tạo ở bước 3.3

---

## 4. Thiết lập AI Server trên Kaggle (Bắt buộc)

Để ứng dụng hoạt động đầy đủ, bạn cần cấu hình AI Server trên Kaggle Notebook với Ollama, FastAPI, và Ngrok.

### 4.1 Tạo Kaggle Notebook

1. Đăng nhập vào: https://www.kaggle.com
2. Click **"Create"** → **"Notebook"**
3. Chọn tên cho notebook, ví dụ: `ptitnotebook-ai-server`
4. **Rất quan trọng:** Thiết lập như sau:
   - **Accelerator:** GPU T4 x 2
   - **Compute Slots:** Theo mặc định (hoặc chọn tối đa nếu bạn có)
   - **Internet:** **BẬT ON** ✓

### 4.2 Cell 1: Cài đặt Dependencies

Chạy cell Bash đầu tiên:

```bash
# Install system dependencies
apt-get update && apt-get install -y zstd wget curl

# Install Python packages
pip install fastapi uvicorn pyngrok nest-asyncio requests
```

### 4.3 Cell 2: Tải và Khởi chạy Ollama

Chạy cell Python:

```python
import subprocess
import os
import time
import asyncio
from nest_asyncio import apply

apply()

# Tải Ollama
print("Downloading Ollama...")
result = subprocess.run(
    'curl -fsSL https://ollama.ai/install.sh | sh',
    shell=True,
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)

# Khởi chạy Ollama service
print("Starting Ollama service...")
subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Chờ Ollama khởi động
time.sleep(10)

# Pull các models cần thiết
print("Pulling nomic-embed-text model...")
subprocess.run(['ollama', 'pull', 'nomic-embed-text'], check=True)

print("Pulling llama3:8b model...")
subprocess.run(['ollama', 'pull', 'llama3:8b'], check=True)

print("Models ready!")
```

**Thời gian chạy:** ~5-10 phút (tùy vào tốc độ mạng và kích thước model)

### 4.4 Cell 3: Tạo FastAPI Application

Chạy cell Python với `%%writefile api.py`:

```python
%%writefile api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
from typing import List

app = FastAPI(title="PtitNotebook AI Server")

OLLAMA_API_BASE = "http://localhost:11434/api"

class EmbedRequest(BaseModel):
    texts: List[str]

class ChatRequest(BaseModel):
    question: str
    context: str = ""

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]

class ChatResponse(BaseModel):
    answer: str

@app.get("/health")
async def health_check():
    """Kiểm tra trạng thái server"""
    return {"status": "ok", "service": "ptitnotebook-ai"}

@app.post("/embed", response_model=EmbedResponse)
async def embed_texts(request: EmbedRequest):
    """
    Nhận danh sách text, trả về vector embeddings.
    Sử dụng model nomic-embed-text
    """
    try:
        embeddings = []
        for text in request.texts:
            response = requests.post(
                f"{OLLAMA_API_BASE}/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text
                }
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data.get("embedding", []))
        
        return EmbedResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Nhận câu hỏi + context, trả về câu trả lời từ llama3:8b
    """
    try:
        prompt = f"""Based on the following context, answer the question.

Context:
{request.context}

Question:
{request.question}

Answer:"""
        
        response = requests.post(
            f"{OLLAMA_API_BASE}/generate",
            json={
                "model": "llama3:8b",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "No response generated")
        
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.5 Cell 4: Khởi chạy FastAPI với Ngrok

Chạy cell Python:

```python
import subprocess
import asyncio
from pyngrok import ngrok
from nest_asyncio import apply
import time

apply()

# Khởi chạy FastAPI server trong background
print("Starting FastAPI server...")
process = subprocess.Popen(
    ['uvicorn', 'api:app', '--host', '0.0.0.0', '--port', '8000'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Chờ server khởi động
time.sleep(5)

# Khởi chạy Ngrok tunnel
print("Starting Ngrok tunnel...")
ngrok_tunnel = ngrok.connect(8000, proto="http")
public_url = ngrok_tunnel.public_url

print("=" * 60)
print("FastAPI Server is running!")
print("=" * 60)
print(f"Local URL:   http://localhost:8000")
print(f"Public URL:  {public_url}")
print("=" * 60)
print("\nCopy the PUBLIC URL above and add it to Django settings.py")
print("=" * 60)

# Keep the process running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    ngrok.kill()
    process.terminate()
```

### 4.6 Sao chép Public URL vào Django Settings

Sau khi Cell 4 chạy xong, bạn sẽ thấy một URL công khai như:

```
Public URL: https://xxxx-xxx-xxx.ngrok.io
```

**Thực hiện các bước sau:**

1. Mở file `core/settings.py` trong Django project
2. Tìm hoặc thêm dòng:
   ```python
   KAGGLE_API_URL = "https://xxxx-xxx-xxx.ngrok.io"
   ```
3. Lưu file

**Ví dụ đầy đủ trong settings.py:**

```python
# AI Server Configuration (Kaggle)
KAGGLE_API_URL = "https://abc123-def456.ngrok.io"  # Thay bằng URL của bạn
```

### 4.7 Kiểm tra Kết nối

Sau khi cập nhật settings.py, hãy test:

```bash
# Trong local terminal
python manage.py shell
```

```python
from notebooks.services import KaggleService

# Test embed endpoint
texts = ["Hello world", "PtitNotebook"]
embeddings = KaggleService.get_embeddings(texts)
print(f"Received {len(embeddings)} embeddings")
```

Nếu thành công, bạn sẽ thấy:
```
Received 2 embeddings
```

---

## 5. Xác Nhận Cài Đặt Hoàn Thành

Để đảm bảo mọi thứ đã sẵn sàng, hãy kiểm tra:

### Phía Local Web App

- ✅ Django server chạy ở `http://localhost:8080`
- ✅ PostgreSQL container/service đang hoạt động
- ✅ ChromaDB container/service đang hoạt động (nếu dùng Docker)
- ✅ Bạn có thể đăng nhập vào `/admin` bằng credentials superuser
- ✅ `KAGGLE_API_URL` được cấu hình trong `core/settings.py`

### Phía Kaggle AI Server

- ✅ Ollama đang chạy với các models `nomic-embed-text` và `llama3:8b`
- ✅ FastAPI server hoạt động ở `localhost:8000` (locally trong Kaggle)
- ✅ Ngrok tunnel đang kết nối với public internet
- ✅ Health check: Truy cập `{PUBLIC_URL}/health` trả về `{"status": "ok", ...}`

### Test End-to-End

1. Tạo user account trên local web app
2. Tạo notebook mới
3. Tải lên một file PDF hoặc TXT
4. Kiểm tra xem file được xử lý mà không có lỗi
5. Gửi một câu hỏi
6. Kiểm tra xem câu trả lời từ AI server được hiển thị

---

## 6. Khắc Phục Sự Cố Thường Gặp

### Vấn đề: `ModuleNotFoundError: No module named 'langchain_text_splitters'`

**Giải pháp:** Ứng dụng sẽ tự động dùng fallback splitter. Để cài đặt module thực:
```bash
pip install pymupdf chromadb requests
pip install langchain-text-splitters
```

### Vấn đề: PostgreSQL connection refused

**Linux/WSL:**
```bash
docker-compose ps  # Kiểm tra container
docker-compose logs postgres  # Xem logs
docker-compose restart postgres  # Khởi động lại
```

**Windows:**
- Kiểm tra xem Docker Desktop đang chạy
- Kiểm tra Windows Services → tìm PostgreSQL

**Windows không Docker:**
- Kiểm tra Windows Services → PostgreSQL phải chạy
- Mở pgAdmin và verify database `ptitnotebook` tồn tại

### Vấn đề: ChromaDB không kết nối

**Docker:**
```bash
docker-compose logs chroma
docker-compose restart chroma
```

**Local mode (Windows không Docker):**
- ChromaDB sẽ tự động tạo folder `chroma_db`
- Kiểm tra permissions

### Vấn đề: Ngrok tunnel bị disconnect

**Giải pháp:**
- Restart Cell 4 trên Kaggle Notebook
- Copy URL mới vào `KAGGLE_API_URL` trong settings.py

### Vấn đề: Ollama models chưa pull xong

**Kiểm tra trạng thái:**
```bash
ollama ls  # Trong Kaggle terminal
```

**Để pull thủ công:**
```bash
ollama pull nomic-embed-text
ollama pull llama3:8b
```

---

## 7. Tài Liệu Tham Khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Ngrok Documentation](https://ngrok.com/docs)

