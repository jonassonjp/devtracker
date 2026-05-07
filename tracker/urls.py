from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/edit/', views.project_edit, name='project_edit'),
    path('api/new-project/', views.api_new_project, name='api_new_project'),
    path('api/start-session/', views.api_start_session, name='api_start_session'),
    path('api/run-server/', views.api_run_server, name='api_run_server'),
    path('api/stop-server/', views.api_stop_server, name='api_stop_server'),
    path('api/end-session/', views.api_end_session, name='api_end_session'),
    path('api/status/', views.api_status, name='api_status'),
]
