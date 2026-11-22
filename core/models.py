from django.conf import settings
from django.db import models
from django.utils import timezone

class ProfessionalProfile(models.Model):
    ROLE_BASIC = "basic"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [(ROLE_BASIC, "Básico"), (ROLE_ADMIN, "Administrador")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="professional_profile")
    role = models.CharField("Nível de acesso", max_length=10, choices=ROLE_CHOICES, default=ROLE_BASIC)
    is_professional = models.BooleanField("Atua como profissional", default=True)
    specialty = models.ForeignKey("Specialty", on_delete=models.SET_NULL, null=True, blank=True, related_name="professionals")
    registration = models.CharField("Registro profissional", max_length=80, blank=True)
    public_bio = models.TextField("Apresentação pública", blank=True)
    show_on_site = models.BooleanField("Exibir no site público", default=False)
    can_access_records = models.BooleanField("Pode acessar prontuários", default=False)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Perfil profissional"
        verbose_name_plural = "Perfis profissionais"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_admin(self):
        return self.user.is_superuser or self.role == self.ROLE_ADMIN


class Specialty(models.Model):
    name = models.CharField("Especialidade / serviço", max_length=120, unique=True)
    description = models.CharField("Descrição", max_length=240, blank=True)
    active = models.BooleanField("Ativa", default=True)
    public_on_site = models.BooleanField("Exibir no site", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.name


class Patient(models.Model):
    SEX_CHOICES = [("F", "Feminino"), ("M", "Masculino"), ("O", "Outro"), ("N", "Não informado")]
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [(STATUS_ACTIVE, "Ativo"), (STATUS_INACTIVE, "Desativado")]

    full_name = models.CharField("Nome completo", max_length=180)
    birth_date = models.DateField("Data de nascimento", null=True, blank=True)
    sex = models.CharField("Sexo", max_length=1, choices=SEX_CHOICES, default="N")
    cpf = models.CharField("CPF", max_length=14, blank=True)
    no_cpf = models.BooleanField("Não possui CPF", default=False)
    phone = models.CharField("Telefone", max_length=30, blank=True)
    email = models.EmailField("E-mail", blank=True)

    self_guardian = models.BooleanField("O próprio paciente é responsável", default=True)
    guardian_name = models.CharField("Nome do responsável", max_length=180, blank=True)
    guardian_age = models.PositiveSmallIntegerField("Idade do responsável", null=True, blank=True)
    guardian_birth_date = models.DateField("Nascimento do responsável", null=True, blank=True)
    guardian_relationship = models.CharField("Grau de parentesco", max_length=80, blank=True)
    guardian_profession = models.CharField("Profissão do responsável", max_length=120, blank=True)

    street = models.CharField("Rua e número", max_length=200, blank=True)
    neighborhood = models.CharField("Bairro", max_length=120, blank=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    notes = models.TextField("Observações administrativas", blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="patients_created")
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.localdate()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def guardian_display(self):
        return self.full_name if self.self_guardian else self.guardian_name


class Room(models.Model):
    name = models.CharField("Nome da sala", max_length=80, unique=True)
    active = models.BooleanField("Ativa", default=True)
    def __str__(self):
        return self.name


class ProfessionalAvailability(models.Model):
    WEEKDAYS = [(0, "Segunda-feira"), (1, "Terça-feira"), (2, "Quarta-feira"), (3, "Quinta-feira"), (4, "Sexta-feira"), (5, "Sábado"), (6, "Domingo")]
    MODALITIES = [("presencial", "Presencial"), ("online", "Online"), ("domicilio", "Domicílio")]
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="availability_rules")
    weekday = models.PositiveSmallIntegerField("Dia da semana", choices=WEEKDAYS)
    start_time = models.TimeField("Início")
    end_time = models.TimeField("Fim")
    modality = models.CharField("Modalidade", max_length=12, choices=MODALITIES, default="presencial")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sala")
    active = models.BooleanField("Ativo", default=True)

    class Meta:
        ordering = ["weekday", "start_time"]
        verbose_name = "Disponibilidade profissional"
        verbose_name_plural = "Disponibilidades profissionais"

    def __str__(self):
        return f"{self.professional} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Agendada"), ("confirmed", "Confirmada"), ("waiting", "Aguardando"),
        ("completed", "Realizada"), ("cancelled", "Cancelada"), ("no_show", "Não compareceu"),
    ]
    MODALITIES = [("presencial", "Presencial"), ("online", "Online"), ("domicilio", "Domicílio")]

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments", verbose_name="Paciente")
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="appointments", verbose_name="Profissional")
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="appointments", verbose_name="Serviço / especialidade")
    appointment_date = models.DateField("Data")
    start_time = models.TimeField("Horário de início")
    end_time = models.TimeField("Horário final", null=True, blank=True)
    modality = models.CharField("Modalidade", max_length=12, choices=MODALITIES, default="presencial")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sala")
    status = models.CharField("Status", max_length=12, choices=STATUS_CHOICES, default="scheduled")
    observation = models.TextField("Observação administrativa", blank=True)
    cancellation_reason = models.CharField("Motivo do cancelamento", max_length=250, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments_cancelled")
    cancelled_at = models.DateTimeField("Cancelado em", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments_created")
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        ordering = ["appointment_date", "start_time"]
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"

    def __str__(self):
        return f"{self.patient} - {self.appointment_date} {self.start_time}"


class AttendanceTemplate(models.Model):
    name = models.CharField("Nome do modelo", max_length=120)
    body = models.TextField("Texto do documento")
    active = models.BooleanField("Ativo", default=True)
    is_deleted = models.BooleanField("Excluído", default=False)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Modelo de declaração"
        verbose_name_plural = "Modelos de declaração"

    def __str__(self):
        return self.name


class AttendanceDeclaration(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="declarations")
    template = models.ForeignKey(AttendanceTemplate, on_delete=models.PROTECT, related_name="issued_declarations")
    patient_name_snapshot = models.CharField("Paciente", max_length=180)
    date_snapshot = models.DateField("Data da consulta")
    start_snapshot = models.TimeField("Início")
    end_snapshot = models.TimeField("Fim", null=True, blank=True)
    body_snapshot = models.TextField("Texto emitido")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    issued_at = models.DateTimeField("Emitida em", auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "Declaração emitida"
        verbose_name_plural = "Declarações emitidas"


class ClinicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="clinical_records")
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="clinical_records")
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="clinical_records")
    content = models.TextField("Registro clínico")
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Registro clínico"
        verbose_name_plural = "Registros clínicos"


class AuditEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField("Ação", max_length=80)
    object_type = models.CharField("Tipo", max_length=80)
    object_id = models.CharField("Identificador", max_length=40, blank=True)
    summary = models.CharField("Resumo", max_length=255)
    created_at = models.DateTimeField("Data e hora", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Registro de auditoria"
        verbose_name_plural = "Registros de auditoria"

    def __str__(self):
        return f"{self.action} - {self.object_type} - {self.created_at}"
