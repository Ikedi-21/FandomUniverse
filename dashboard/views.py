from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.


@user_passes_test(lambda user: user.is_staff)
def admin_overview(request):
 


  return render(request, "admin-overview.html")

@user_passes_test(lambda user: user.is_staff)
def admin_submisions_queue_view(request):
 
  
  return render(request, "admin-submissions-queue.html")
  
@user_passes_test(lambda user: user.is_staff)
def admin_chatbot_faq_view(request):
 

  return render(request, "admin-chatbot-faq.html")

@user_passes_test(lambda user: user.is_staff)
def admin_content_form_view(request):
 

  return render(request, "admin-content-form.html")


@login_required
def user_dashboard_view(request):


  return render(request, "dashboard.html")
