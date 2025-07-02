from django.urls import path
from . import views

urlpatterns = [
    path('heartbeat/', views.Heartbeat.as_view()),
    path('commands/<int:pk>/result/', views.CommandResult.as_view()),
    path('agents/', views.AgentList.as_view()),
]