from django.db import models
from django.contrib.auth.models import User

# Sổ ghi chú
class Notebook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Nguồn tài liệu
class Document(models.Model):
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/')
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name

# Lịch sử hội thoại
class ChatHistory(models.Model):
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Ghi chú đã lưu
class SavedAnswer(models.Model):
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)
    summary = models.CharField(max_length=150)
    full_content = models.TextField()
    saved_at = models.DateTimeField(auto_now_add=True)