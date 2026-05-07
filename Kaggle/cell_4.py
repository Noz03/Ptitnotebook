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