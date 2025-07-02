from django.urls import path
from . import views

urlpatterns = [
    # heartbeat
    path('heartbeat/', views.Heartbeat.as_view()),
    # commands
    path('commands/<int:pk>/result/', views.CommandResult.as_view()),
    path('commands/server/<str:uuid>/', views.CommandServerList.as_view()),
    path('commands/create/', views.CommandCreate.as_view()),
    # agents
    path('agents/', views.AgentList.as_view()),
    # metrics
    path('metrics/<int:pk>/', views.MetricDetail.as_view()),
    path('metrics/server/<str:uuid>/', views.MetricServerDetail.as_view()),
    # inventory
    path('inventory/<int:pk>/', views.InventoryDetail.as_view()),
    path('inventory/server/<str:uuid>/', views.InventoryServerDetail.as_view()),
]