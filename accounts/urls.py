from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('create/', views.create_post, name='create_post'),
    path('edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('<int:pk>/comment/', views.create_comment, name='create_comment'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('user/<int:pk>/posts/', views.UserPostsView.as_view(), name='user_posts'),
    path('profile/<int:pk>/', views.user_profile, name='user_profile'),
    path('contact/', views.contact_view, name='contact'),
]
