from django.urls import path
from .views import RegisterView,CustomLoginView,Dashboard,Logout,ChangePasswordView,ProfileView
urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('', CustomLoginView.as_view(), name='login'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', Logout.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
