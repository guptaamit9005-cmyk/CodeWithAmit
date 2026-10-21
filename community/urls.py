from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.doubt_list, name='doubt_list'),
    path('ask/', views.ask_doubt, name='ask_doubt'),
    path('question/<slug:slug>/', views.doubt_detail, name='doubt_detail'),
    path('question/<slug:slug>/answer/', views.post_answer, name='post_answer'),
    path('question/<int:question_id>/upvote/', views.toggle_question_upvote, name='toggle_question_upvote'),
    path('answer/<int:answer_id>/upvote/', views.toggle_answer_upvote, name='toggle_answer_upvote'),
    path('answer/<int:answer_id>/accept/', views.accept_answer, name='accept_answer'),
]
