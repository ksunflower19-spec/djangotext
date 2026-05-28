from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('temporary/', views.temporary_storage, name='temporary'),
    path('exhibition/', views.exhibition, name='exhibition'),
    path('content/create/', views.create, name='create_content'),
    path('content/<int:pk>/', views.detail, name='detail'),
    path('content/<int:pk>/edit/verify/', views.edit_verify, name='edit_verify'),
    path('content/<int:pk>/edit/', views.edit, name='edit_content'),
    path('content/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('content/<int:pk>/reaction/', views.toggle_reaction, name='toggle_reaction'),
    path('content/<int:pk>/vote/', views.cast_vote, name='cast_vote'),
    path('content/<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
]
