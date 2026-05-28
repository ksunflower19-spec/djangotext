from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='noticeboard_index'),
    path('new/', views.create, name='noticeboard_create'),
    path('<int:pk>/', views.detail, name='noticeboard_detail'),
]
