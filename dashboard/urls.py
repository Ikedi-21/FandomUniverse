from django.urls import path
from . import views

urlpatterns = [
    #Admin dashboard views
    path('admin/', views.admin_overview, name="admin_overview"),
    path('admin/submissions/', views.admin_submisions_queue_view, name="admin_submissions"),
    path('admin/chatbot-faq/', views.admin_chatbot_faq_view, name="admin_chatbot_faq"),
    path('admin/content-form/', views.admin_content_form_view, name="admin_content_form"),

    #User dashboard view
    path('', views.user_dashboard_view, name="user_dashboard"),
]
