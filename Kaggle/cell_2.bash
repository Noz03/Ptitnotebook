import subprocess
import time

# 1. Khởi chạy máy chủ Ollama chạy ngầm
print("Đang khởi động Ollama...")
subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Đợi 5 giây để hệ thống Ollama ổn định trước khi tải model
time.sleep(5)

# 2. Tải mô hình chuyển đổi văn bản thành Vector (Embedding)
print("Đang tải nomic-embed-text...")
!ollama pull nomic-embed-text

# 3. Tải mô hình Ngôn ngữ lớn (LLM) để trả lời câu hỏi
print("Đang tải llama3:8b...")
!ollama pull llama3:8b