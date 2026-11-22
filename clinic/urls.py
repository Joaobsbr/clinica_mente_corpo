from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.home, name="home"),

    path("recepcao/", views.recepcao, name="recepcao"),
    path("pacientes/", views.pacientes, name="pacientes"),
    path("pacientes/novo/", views.paciente_novo, name="paciente_novo"),
    path("pacientes/<int:pk>/editar/", views.paciente_editar, name="paciente_editar"),

    path("agenda/", views.agenda, name="agenda"),
    path("agenda/agendar/", views.agendamento_novo, name="agendamento_novo"),
    path("agenda/disponibilidade/", views.disponibilidade, name="disponibilidade"),
    path("agenda/disponibilidade/nova/", views.disponibilidade_nova, name="disponibilidade_nova"),
    path("agenda/disponibilidade/<int:pk>/alternar/", views.disponibilidade_alternar, name="disponibilidade_alternar"),
    path("agenda/<int:pk>/cancelar/", views.agendamento_cancelar, name="agendamento_cancelar"),

    path("consultas/", views.consultas, name="consultas"),
    path("consultas/<int:pk>/realizada/", views.consulta_realizar, name="consulta_realizar"),
    path("consultas/<int:pk>/declaracao/", views.emitir_declaracao, name="emitir_declaracao"),
    path("declaracoes/<int:pk>/imprimir/", views.imprimir_declaracao, name="imprimir_declaracao"),

    path("profissionais/", views.profissionais, name="profissionais"),
    path("profissionais/novo/", views.profissional_novo, name="profissional_novo"),
    path("profissionais/<int:pk>/editar/", views.profissional_editar, name="profissional_editar"),

    path("prontuarios/", views.prontuarios, name="prontuarios"),
    path("prontuarios/novo/", views.prontuario_novo, name="prontuario_novo"),

    path("administracao/", views.administracao, name="administracao"),
    path("administracao/modelos/novo/", views.modelo_documento_novo, name="modelo_documento_novo"),
    path("administracao/modelos/<int:pk>/editar/", views.modelo_documento_editar, name="modelo_documento_editar"),
    path("administracao/modelos/<int:pk>/alternar/", views.modelo_documento_alternar, name="modelo_documento_alternar"),
    path("administracao/modelos/<int:pk>/excluir/", views.modelo_documento_excluir, name="modelo_documento_excluir"),
    path("administracao/especialidades/", views.especialidades_admin, name="especialidades_admin"),
    path("administracao/especialidades/nova/", views.especialidade_nova, name="especialidade_nova"),
    path("administracao/salas/", views.salas_admin, name="salas_admin"),
    path("administracao/salas/nova/", views.sala_nova, name="sala_nova"),
    path("administracao/auditoria/", views.auditoria, name="auditoria"),
]
