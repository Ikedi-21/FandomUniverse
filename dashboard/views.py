from django.shortcuts import render, redirect

# Create your views here.


def admin_overview(request):
 


  return render(request, "admin-overview.html")

def admin_submisions_queue_view(request):
 
  
  return render(request, "admin-submissions-queue.html")
  
def admin_chatbot_faq_view(request):
 

  return render(request, "admin-chatbot-faq.html")

def admin_content_form_view(request):
 

  return render(request, "admin-content-form.html")


def user_dashboard_view(request):


  return render(request, "dashboard.html")