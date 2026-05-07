# 1. Cập nhật hệ thống và cài đặt gói giải nén zstd
!apt-get update && apt-get install -y zstd

# 2. Cài đặt các thư viện Python cho API và Tunneling
!pip install fastapi uvicorn pyngrok nest-asyncio

# 3. Tải và cài đặt hệ thống Ollama
!curl -fsSL https://ollama.com/install.sh | sh