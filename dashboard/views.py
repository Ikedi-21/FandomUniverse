from django.shortcuts import render, redirect

# Create your views here.


def admin_overview(request):
  if not request.user.is_authenticated and not request.user.is_superuser and not request.user.role == "admin":
    return redirect("home")


  return render(request, "admin-overview.html")

def admin_submisions_queue_view(request):
  if not request.user.is_authenticated and not request.user.is_superuser and not request.user.role == "admin":
    return redirect("home")
  
  return render(request, "admin-submissions-queue.html")
  
def admin_chatbot_faq_view(request):
  if not request.user.is_authenticated and not request.user.is_superuser and not request.user.role == "admin":
    return redirect("home")

  return render(request, "admin-chatbot-faq.html")

def admin_content_form_view(request):
  if not request.user.is_authenticated and not request.user.is_superuser and not request.user.role == "admin":
    return redirect("home")

  return render(request, "admin-content-form.html")


