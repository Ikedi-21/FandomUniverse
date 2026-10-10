from django.urls import path
from . import views

urlpatterns = [
    # Admin dashboard views
    path('admin/', views.admin_overview, name="admin_overview"),
    path('admin/overview/', views.admin_overview, name="admin-overview"),
    path('admin/submissions/', views.admin_submisions_queue_view, name="admin_submissions"),
    path('admin/submissions/queue/', views.admin_submisions_queue_view, name="admin-submissions-queue"),
    path('admin/chatbot-faq/', views.admin_chatbot_faq_view, name="admin_chatbot_faq"),
    path('admin/faq/', views.admin_chatbot_faq_view, name="admin-chatbot-faq"),
    path('admin/content-form/', views.admin_content_form_view, name="admin_content_form"),
    path('admin/content/new/', views.admin_content_form_view, name="admin-content-form"),

    # User dashboard view
    path('', views.user_dashboard_view, name="user_dashboard"),
    path('home/', views.user_dashboard_view, name="dashboard"),
]

