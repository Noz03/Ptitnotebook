from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notebooks.urls')), # Trỏ toàn bộ đường dẫn về app notebooks
]

# Cấu hình để xem được file PDF trên trình duyệt lúc code
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)