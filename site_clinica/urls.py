from django.urls import path
<<<<<<< HEAD
=======
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
>>>>>>> 831f6ac6766c90c5f813e3257a749811e6e8055f
from . import views

urlpatterns = [
    path('', views.index, name='index.html'),
    path('dashboard', views.dashboard, name='dashboard.html'),
<<<<<<< HEAD
=======
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
>>>>>>> 831f6ac6766c90c5f813e3257a749811e6e8055f
]