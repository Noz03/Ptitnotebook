from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('notebook/<int:pk>/', views.workspace, name='workspace'),
    path('notebook/<int:pk>/rename/', views.rename_notebook, name='rename_notebook'),
    path('notebook/<int:pk>/delete/', views.delete_notebook, name='delete_notebook'),
    path('notebook/<int:pk>/chat/', views.chat_ajax, name='chat_ajax'),
    path('notebook/<int:pk>/save-answer/', views.save_answer_ajax, name='save_answer_ajax'),
    path('notebook/<int:pk>/saved-answer/<int:answer_pk>/export/', views.export_saved_answer, name='export_saved_answer'),
    path('notebook/<int:pk>/saved-answer/<int:answer_pk>/delete/', views.delete_saved_answer, name='delete_saved_answer'),
]