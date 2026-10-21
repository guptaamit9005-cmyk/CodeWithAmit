from django.urls import path
from . import views

app_name = 'coding_practice'

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('add/', views.add_question, name='add_question'),

    # Practice Sets (Course-like tracks)
    path('sets/add/', views.add_practice_set, name='add_practice_set'),
    path('sets/<slug:slug>/', views.practice_set_detail, name='practice_set_detail'),
    path('sets/<slug:slug>/edit/', views.edit_practice_set, name='edit_practice_set'),
    path('sets/<slug:slug>/delete/', views.delete_practice_set, name='delete_practice_set'),

    # Contests
    path('contests/', views.contest_list, name='contest_list'),
    path('contests/<slug:slug>/', views.contest_detail, name='contest_detail'),
    path('contests/<slug:slug>/register/', views.register_contest, name='register_contest'),
    path('contests/<slug:slug>/leaderboard/', views.contest_leaderboard, name='contest_leaderboard'),

    # Discussions
    path('discussions/<int:discussion_id>/upvote/', views.toggle_discussion_upvote, name='toggle_discussion_upvote'),
    path('discussions/<int:discussion_id>/comment/', views.add_discussion_comment, name='add_discussion_comment'),

    # Code Editor & Compiler Sandbox
    path('editor/', views.code_editor, name='code_editor'),
    path('compiler/', views.code_editor, name='compiler'),
    path('sandbox/run/', views.run_sandbox_code, name='run_sandbox_code'),
    path('sandbox/save/', views.save_code_snippet, name='save_code_snippet'),
    path('sandbox/snippet/<int:snippet_id>/', views.load_code_snippet_api, name='load_code_snippet_api'),
    path('sandbox/snippet/<int:snippet_id>/delete/', views.delete_code_snippet, name='delete_code_snippet'),

    # Problem details and actions
    path('<slug:slug>/', views.problem_detail, name='problem_detail'),
    path('<slug:slug>/edit/', views.edit_question, name='edit_question'),
    path('<slug:slug>/delete/', views.delete_question, name='delete_question'),
    path('<slug:slug>/toggle-solved/', views.toggle_solved, name='toggle_solved'),
    path('<slug:slug>/run/', views.run_code, name='run_code'),
    path('<slug:slug>/submit/', views.submit_code, name='submit_code'),
    path('<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('<slug:slug>/discuss/', views.create_discussion, name='create_discussion'),
]
