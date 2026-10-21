from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('add-lesson/', views.add_lesson, name='add_lesson'),
    path('add-category/', views.add_category, name='add_category'),
    path('ai-quiz-generator/', views.ai_quiz_generator, name='ai_quiz_generator'),
    path('ai-quiz/', views.ai_quiz_generator, name='ai_quiz_short'),
    path('notes/<int:note_id>/delete/', views.delete_lesson_note, name='delete_lesson_note'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/edit/', views.edit_lesson, name='edit_lesson'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/delete/', views.delete_lesson, name='delete_lesson'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/add-quiz/', views.add_quiz_question, name='add_quiz_question'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/complete/', views.complete_lesson, name='complete_lesson'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/quiz-submit/', views.submit_quiz, name='submit_quiz'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/add-note/', views.add_lesson_note, name='add_lesson_note'),
]
