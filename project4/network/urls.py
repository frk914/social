
from django.urls import path

from . import views


urlpatterns = [
    # path("", views.index, name="index"),
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/create/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path('post/<int:pk>/like/', views.LikeView.as_view(), name='post-like'),
    path('user/<int:user_id>/',views.UserProfileView.as_view(), name='user-profile'),
    path('follow-user/<int:user_id>/', views.follow_user, name='follow_user'),
    path('userlist', views.user_list, name='user-list'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

]


