from django.urls import path
from . import views

app_name = 'article'
urlpatterns = [
<<<<<<< HEAD
    path('', views.article_list, name='article-list'),
    path('<slug:slug>/', views.article_detail, name='article-detail'),
]
=======
    path('articles/', views.article_list, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('highlights/', views.highlight_list, name='highlight_list'),
    path('submit/', views.submit_content, name='submit_content'),
    path('submit/mine/', views.my_submissions, name='my_submissions'),

    path('manage/submissions/', views.submissions_queue, name='submissions_queue'),
    path('manage/submissions/<int:pk>/approve/', views.approve_submission, name='approve_submission'),
    path('manage/submissions/<int:pk>/reject/', views.reject_submission, name='reject_submission'),
    path('manage/highlights/', views.highlight_manage, name='highlight_manage'),
    path('manage/highlights/new/', views.highlight_form, name='highlight_new'),
    path('manage/highlights/<int:pk>/edit/', views.highlight_form, name='highlight_edit'),
    path('manage/highlights/<int:pk>/delete/', views.highlight_delete, name='highlight_delete'),
]
>>>>>>> d63f555ee2c6f7c766590cb65937d873d683fb6e
