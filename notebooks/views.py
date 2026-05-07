from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Notebook, Document, ChatHistory, SavedAnswer
from .services import DocumentService, VectorDBService, KaggleService
# Các hàm xác thực

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu!')
    return render(request, 'notebooks/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        cp = request.POST.get('confirm_password')
        if p != cp:
            messages.error(request, 'Mật khẩu không khớp!')
        elif User.objects.filter(username=u).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
        else:
            User.objects.create_user(username=u, password=p)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('login')
    return render(request, 'notebooks/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user 
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            new_note = Notebook.objects.create(user=user, name=name)
            return redirect('workspace', pk=new_note.id)
    notebooks = Notebook.objects.filter(user=user).order_by('-last_accessed')
    return render(request, 'notebooks/dashboard.html', {'notebooks': notebooks})

@login_required
def workspace(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    notebook.save() 

    # UPLOAD TÀI LIỆU 
    if request.method == 'POST' and request.FILES.get('document'):
        uploaded_file = request.FILES['document']
        
        # 1. Lưu bản ghi vào PostgreSQL
        doc = Document.objects.create(
            notebook=notebook,
            file_name=uploaded_file.name,
            file_path=uploaded_file
        )

        # 2. Tiền xử lý văn bản (Ingestion Pipeline)
        try:
            # Lấy đường dẫn vật lý của file vừa lưu
            file_full_path = doc.file_path.path
            
            # Gọi DocumentService để băm nhỏ file
            chunks = DocumentService.process_and_chunk_pdf(file_full_path, doc.file_name)
            
            # Gọi VectorDBService để gửi lên Kaggle và lưu vào ChromaDB
            vector_service = VectorDBService()
            vector_service.save_chunks_to_db(chunks)
            
            # Mặc định chọn tài liệu này làm nguồn sau khi upload thành công
            doc.is_selected = True
            doc.save()
            
        except Exception as e:
            # Nếu có lỗi, xóa bản ghi để đảm bảo sạch dữ liệu
            doc.delete()
            from django.contrib import messages
            messages.error(request, f"Lỗi xử lý AI: {str(e)}")

        return redirect('workspace', pk=notebook.id)

    # LẤY DỮ LIỆU
    documents = Document.objects.filter(notebook=notebook)
    chat_history = ChatHistory.objects.filter(notebook=notebook).order_by('created_at')
    saved_answers = SavedAnswer.objects.filter(notebook=notebook).order_by('-saved_at')

    context = {
        'notebook': notebook,
        'documents': documents,
        'chat_history': chat_history,
        'saved_answers': saved_answers,
    }
    return render(request, 'notebooks/workspace.html', context)

@login_required
@require_POST
def rename_notebook(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    new_name = request.POST.get('new_name', '').strip()
    if new_name:
        notebook.name = new_name
        notebook.save()
        messages.success(request, 'Notebook đã được đổi tên thành công.')
    else:
        messages.error(request, 'Tên notebook không được để trống.')
    return redirect('workspace', pk=notebook.id)

@login_required
@require_POST
def delete_notebook(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    notebook.delete()
    messages.success(request, 'Notebook đã được xóa.')
    return redirect('dashboard')

@login_required
@require_POST
def chat_ajax(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    question = request.POST.get('question', '').strip()
    if not question:
        return JsonResponse({'error': 'Question is required.'}, status=400)

    selected_docs = Document.objects.filter(notebook=notebook, is_selected=True)
    if not selected_docs.exists():
        return JsonResponse({'error': 'No selected documents found.'}, status=400)

    answer = 'This is a mock AI response.'
    ChatHistory.objects.create(notebook=notebook, question=question, answer=answer)
    return JsonResponse({'question': question, 'answer': answer})

@login_required
@require_POST
def save_answer_ajax(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    answer_text = request.POST.get('answer_text', '').strip()
    if not answer_text:
        return JsonResponse({'error': 'Answer text is required.'}, status=400)

    summary = answer_text[:100]
    SavedAnswer.objects.create(notebook=notebook, summary=summary, full_content=answer_text)
    return JsonResponse({'status': 'success', 'summary': summary, 'full_content': answer_text})

@login_required
def export_saved_answer(request, pk, answer_pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    saved_answer = get_object_or_404(SavedAnswer, pk=answer_pk, notebook=notebook)
    response = HttpResponse(saved_answer.full_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="saved_answer_{saved_answer.id}.txt"'
    return response

@login_required
@require_POST
def delete_saved_answer(request, pk, answer_pk):
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    saved_answer = get_object_or_404(SavedAnswer, pk=answer_pk, notebook=notebook)
    saved_answer.delete()
    return JsonResponse({'status': 'success'})

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
        # Tìm kiếm ngữ cảnh
        vector_db = VectorDBService()
        search_results = vector_db.search_similar_chunks(question, top_k=3)
        
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