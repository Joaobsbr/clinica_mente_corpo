from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('agenda/', views.agenda, name='agenda'),
    path('consultas/', views.consultas, name='consultas'),
    path('especialidades/', views.especialidades, name='especialidades'),
    path('financeiro/', views.financeiro, name='financeiro'),
    path('pacientes/', views.pacientes, name='pacientes'),
    path('profissionais/', views.profissionais, name='profissionais'),
    path('prontuarios/', views.prontuarios, name='prontuarios'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]