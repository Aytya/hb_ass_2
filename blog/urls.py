from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health, name='health'),
    path('list/', views.post_list, name='post_list'),
    path('list/<int:pk>/', views.post_detail, name='post_detail'),
    path('list/add/', views.post_new, name='post_add'),
    path('list/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('list/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('list/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]