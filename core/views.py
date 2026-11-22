import csv
from datetime import datetime, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Patient, Appointment, Room, Specialty, ProfessionalProfile,
    ProfessionalAvailability, AttendanceTemplate, AttendanceDeclaration,
    AuditEvent, ClinicalRecord
)
from .forms import (
    PatientForm, AppointmentForm, ProfessionalCreateForm, ProfessionalEditForm,
    AvailabilityForm, AttendanceTemplateForm, SpecialtyForm, RoomForm,
    ClinicalRecordForm
)
from .services import log_event, appointment_conflict, render_attendance_text

User = get_user_model()
CLINIC_NAME = "Espaço Mente e Corpo"
CLINIC_ADDRESS = "Avenida São Paulo, nº 206 — Jardim São Paulo, Recife/PE"

def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.professional_profile.role == ProfessionalProfile.ROLE_ADMIN
    except ProfessionalProfile.DoesNotExist:
        return False

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not is_admin(request.user):
            return HttpResponseForbidden("Você não tem permissão para acessar esta área.")
        return view_func(request, *args, **kwargs)
    return wrapped

def clinical_access_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        allowed = is_admin(request.user)
        if not allowed:
            try:
                allowed = request.user.professional_profile.can_access_records
            except ProfessionalProfile.DoesNotExist:
                allowed = False
        if not allowed:
            return HttpResponseForbidden("Seu perfil não está autorizado a acessar prontuários.")
        return view_func(request, *args, **kwargs)
    return wrapped

def home(request):
    if request.user.is_authenticated:
        return redirect("recepcao")
    specialties = Specialty.objects.filter(active=True, public_on_site=True)
    professionals = ProfessionalProfile.objects.filter(
        user__is_active=True, is_professional=True, show_on_site=True
    ).select_related("user", "specialty")
    return render(request, "core/home.html", {
        "specialties": specialties,
        "professionals": professionals,
        "whatsapp": "5581991523595",
        "clinic_address": CLINIC_ADDRESS,
    })

@login_required
def recepcao(request):
    q = request.GET.get("q", "").strip()
    patients = Patient.objects.all()
    if q:
        patients = patients.filter(Q(full_name__icontains=q) | Q(guardian_name__icontains=q))
    return render(request, "core/recepcao.html", {
        "patients": patients[:100], "q": q,
        "result_count": patients.count() if q else 0,
    })

@login_required
def pacientes(request):
    q = request.GET.get("q", "").strip()
    qs = Patient.objects.all()
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(guardian_name__icontains=q) | Q(cpf__icontains=q) | Q(phone__icontains=q))
    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="pacientes.csv"'
        response.write("\ufeff")
        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Nome", "Nascimento", "Idade", "Sexo", "CPF", "Telefone", "Responsável", "Rua e número", "Bairro", "Status"])
        for p in qs:
            writer.writerow([p.full_name, p.birth_date or "", p.age if p.age is not None else "", p.get_sex_display(), "Não possui" if p.no_cpf else p.cpf, p.phone, p.guardian_display, p.street, p.neighborhood, p.get_status_display()])
        return response
    return render(request, "core/pacientes.html", {
        "patients": qs,
        "q": q,
        "total": Patient.objects.count(),
        "active": Patient.objects.filter(status="active").count(),
        "inactive": Patient.objects.filter(status="inactive").count(),
    })

@login_required
def paciente_novo(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            log_event(request.user, "Cadastro", patient, "Paciente cadastrado.")
            messages.success(request, "Paciente cadastrado com sucesso.")
            return redirect("recepcao")
    else:
        form = PatientForm()
    return render(request, "core/paciente_form.html", {"form": form, "title": "Novo paciente"})

@login_required
def paciente_editar(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            log_event(request.user, "Edição", patient, "Cadastro administrativo do paciente atualizado.")
            messages.success(request, "Dados do paciente atualizados.")
            return redirect("recepcao")
    else:
        form = PatientForm(instance=patient)
    return render(request, "core/paciente_form.html", {"form": form, "title": "Editar paciente", "patient": patient})

@login_required
def agenda(request):
    date_value = request.GET.get("date") or timezone.localdate().isoformat()
    try:
        selected_date = datetime.strptime(date_value, "%Y-%m-%d").date()
    except ValueError:
        selected_date = timezone.localdate()

    view_mode = request.GET.get("view", "general")
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    professional_id = request.GET.get("professional", "")

    professionals = User.objects.filter(
        is_active=True, professional_profile__is_professional=True
    ).order_by("first_name", "username")

    if view_mode == "individual":
        if is_admin(request.user):
            professionals_selected = professionals.filter(pk=professional_id) if professional_id else professionals
        else:
            professionals_selected = professionals.filter(pk=request.user.pk)
            professional_id = str(request.user.pk)
    else:
        professionals_selected = professionals
        if professional_id:
            professionals_selected = professionals_selected.filter(pk=professional_id)

    appointments = Appointment.objects.select_related(
        "patient", "professional", "room", "specialty"
    ).filter(appointment_date=selected_date, professional__in=professionals_selected)

    if q:
        appointments = appointments.filter(Q(patient__full_name__icontains=q) | Q(patient__guardian_name__icontains=q))
    if status:
        appointments = appointments.filter(status=status)

    weekday = selected_date.weekday()
    availability_rules = ProfessionalAvailability.objects.filter(
        active=True, weekday=weekday, professional__in=professionals_selected
    ).select_related("professional", "room")

    # Each recurring availability window is displayed, along with the bookings
    # that occupy the corresponding time. The grid is a reference, not a slot-reservation engine.
    availability_rows = []
    booked = list(appointments)
    for rule in availability_rules:
        rule_bookings = sorted(
            [
                a for a in booked
                if a.professional_id == rule.professional_id
                and a.status not in ["cancelled", "no_show"]
                and a.end_time is not None
                and a.start_time < rule.end_time
                and a.end_time > rule.start_time
            ],
            key=lambda a: a.start_time,
        )
        free_intervals = []
        cursor = datetime.combine(selected_date, rule.start_time)
        window_end = datetime.combine(selected_date, rule.end_time)
        for booking in rule_bookings:
            busy_start = datetime.combine(selected_date, booking.start_time)
            busy_end = datetime.combine(selected_date, booking.end_time)
            if busy_start > cursor:
                free_intervals.append({
                    "start": cursor.time(),
                    "end": min(busy_start, window_end).time(),
                })
            cursor = max(cursor, busy_end)
            if cursor >= window_end:
                break
        if cursor < window_end:
            free_intervals.append({"start": cursor.time(), "end": window_end.time()})
        availability_rows.append({
            "rule": rule,
            "appointments": rule_bookings,
            "free_intervals": free_intervals,
        })

    return render(request, "core/agenda.html", {
        "appointments": appointments,
        "selected_date": selected_date,
        "q": q,
        "status": status,
        "professionals": professionals,
        "professional_id": professional_id,
        "view_mode": view_mode,
        "status_choices": Appointment.STATUS_CHOICES,
        "availability_rows": availability_rows,
        "weekday_name": selected_date.strftime("%A"),
    })

@login_required
def agendamento_novo(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.created_by = request.user
            if not appt.end_time:
                appt.end_time = (datetime.combine(appt.appointment_date, appt.start_time) + timedelta(minutes=50)).time()
            conflict = appointment_conflict(appt)
            if conflict:
                form.add_error(None, conflict)
            else:
                appt.save()
                log_event(request.user, "Agendamento", appt, f"Agendamento criado para {appt.patient.full_name}.")
                messages.success(request, "Consulta agendada com sucesso.")
                return redirect("agenda")
    else:
        initial = {}
        if request.GET.get("date"):
            initial["appointment_date"] = request.GET["date"]
        if request.GET.get("patient"):
            initial["patient"] = request.GET["patient"]
        if not is_admin(request.user):
            initial["professional"] = request.user.pk
        form = AppointmentForm(initial=initial, user=request.user)
    return render(request, "core/agendamento_form.html", {"form": form})

@login_required
def agendamento_cancelar(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if appt.status in ["cancelled", "completed", "no_show"]:
        messages.error(request, "Esta consulta não pode ser cancelada neste estado.")
        return redirect("agenda")
    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        detail = request.POST.get("detail", "").strip()
        if detail:
            reason = f"{reason}: {detail}"[:250]
        confirmation = request.POST.get("confirmation", "").strip().upper()
        if confirmation != "CANCELAR" or not reason:
            messages.error(request, "Informe o motivo e digite CANCELAR para confirmar.")
        else:
            appt.status = "cancelled"
            appt.cancellation_reason = reason
            appt.cancelled_by = request.user
            appt.cancelled_at = timezone.now()
            appt.save()
            log_event(request.user, "Cancelamento", appt, f"Consulta cancelada. Motivo: {reason}")
            messages.success(request, "Consulta cancelada. O registro foi mantido no histórico.")
            return redirect("agenda")
    return render(request, "core/cancelar_agendamento.html", {"appointment": appt})

@login_required
def disponibilidade(request):
    profiles = User.objects.filter(is_active=True, professional_profile__is_professional=True)
    rules = ProfessionalAvailability.objects.select_related("professional", "room").filter(active=True)
    if not is_admin(request.user):
        rules = rules.filter(professional=request.user)
        profiles = profiles.filter(pk=request.user.pk)
    elif request.GET.get("professional"):
        rules = rules.filter(professional_id=request.GET["professional"])
    return render(request, "core/disponibilidade.html", {"rules": rules, "professionals": profiles})

@login_required
def disponibilidade_nova(request):
    if request.method == "POST":
        form = AvailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            rule = form.save()
            log_event(request.user, "Disponibilidade", rule, "Disponibilidade semanal cadastrada.")
            messages.success(request, "Disponibilidade cadastrada.")
            return redirect("disponibilidade")
    else:
        form = AvailabilityForm(user=request.user)
    return render(request, "core/disponibilidade_form.html", {"form": form})

@login_required
@require_POST
def disponibilidade_alternar(request, pk):
    rule = get_object_or_404(ProfessionalAvailability, pk=pk)
    if not is_admin(request.user) and rule.professional_id != request.user.pk:
        return HttpResponseForbidden("Você só pode alterar sua própria disponibilidade.")
    rule.active = not rule.active
    rule.save(update_fields=["active"])
    log_event(request.user, "Disponibilidade", rule, "Situação da disponibilidade alterada.")
    messages.success(request, "Disponibilidade atualizada.")
    return redirect("disponibilidade")

@login_required
def consultas(request):
    qs = Appointment.objects.select_related("patient", "professional", "room", "specialty").all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    start = request.GET.get("start", "")
    end = request.GET.get("end", "")
    if q:
        qs = qs.filter(Q(patient__full_name__icontains=q) | Q(patient__guardian_name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if start:
        qs = qs.filter(appointment_date__gte=start)
    if end:
        qs = qs.filter(appointment_date__lte=end)
    templates = AttendanceTemplate.objects.filter(active=True, is_deleted=False)
    return render(request, "core/consultas.html", {
        "appointments": qs, "q": q, "status": status, "start": start, "end": end,
        "status_choices": Appointment.STATUS_CHOICES, "attendance_templates": templates
    })

@login_required
@require_POST
def consulta_realizar(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if appt.status not in ["cancelled", "completed", "no_show"]:
        appt.status = "completed"
        appt.save()
        log_event(request.user, "Consulta realizada", appt, "Consulta marcada como realizada.")
        messages.success(request, "Consulta marcada como realizada.")
    return redirect("consultas")

@login_required
@require_POST
def emitir_declaracao(request, pk):
    appt = get_object_or_404(Appointment.objects.select_related("patient", "professional", "specialty"), pk=pk)
    if appt.status != "completed":
        messages.error(request, "A declaração só pode ser emitida após a consulta ser marcada como realizada.")
        return redirect("consultas")
    template = get_object_or_404(AttendanceTemplate, pk=request.POST.get("template"), active=True, is_deleted=False)
    text = render_attendance_text(template.body, appt, CLINIC_NAME, CLINIC_ADDRESS)
    declaration = AttendanceDeclaration.objects.create(
        appointment=appt, template=template,
        patient_name_snapshot=appt.patient.full_name,
        date_snapshot=appt.appointment_date,
        start_snapshot=appt.start_time,
        end_snapshot=appt.end_time,
        body_snapshot=text,
        issued_by=request.user,
    )
    log_event(request.user, "Declaração emitida", declaration, f"Declaração de comparecimento emitida para {appt.patient.full_name}.")
    return redirect("imprimir_declaracao", pk=declaration.pk)

@login_required
def imprimir_declaracao(request, pk):
    declaration = get_object_or_404(AttendanceDeclaration, pk=pk)
    return render(request, "core/imprimir_declaracao.html", {"declaration": declaration, "clinic_name": CLINIC_NAME, "clinic_address": CLINIC_ADDRESS})

@admin_required
def profissionais(request):
    users = User.objects.select_related("professional_profile", "professional_profile__specialty").order_by("first_name", "username")
    return render(request, "core/profissionais.html", {"professionals": users})

@admin_required
def profissional_novo(request):
    if request.method == "POST":
        form = ProfessionalCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_event(request.user, "Profissional cadastrado", user, f"Conta criada para {user.username}.")
            messages.success(request, "Profissional cadastrado com sucesso.")
            return redirect("profissionais")
    else:
        form = ProfessionalCreateForm()
    return render(request, "core/profissional_form.html", {"form": form, "title": "Novo profissional"})

@admin_required
def profissional_editar(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = ProfessionalEditForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            log_event(request.user, "Profissional atualizado", user, f"Conta/permissões atualizadas para {user.username}.")
            messages.success(request, "Profissional atualizado.")
            return redirect("profissionais")
    else:
        form = ProfessionalEditForm(user=user)
    return render(request, "core/profissional_form.html", {"form": form, "title": "Editar profissional", "target_user": user})

@clinical_access_required
def prontuarios(request):
    q = request.GET.get("q", "").strip()
    records = ClinicalRecord.objects.select_related("patient", "professional")
    if not is_admin(request.user):
        records = records.filter(professional=request.user)
    if q:
        records = records.filter(Q(patient__full_name__icontains=q))
    return render(request, "core/prontuarios.html", {"records": records, "q": q})

@clinical_access_required
def prontuario_novo(request):
    if request.method == "POST":
        form = ClinicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.professional = request.user
            if not is_admin(request.user):
                record.patient = Patient.objects.get(pk=record.patient_id)
            record.save()
            log_event(request.user, "Registro clínico", record, "Registro clínico criado.")
            messages.success(request, "Registro clínico salvo.")
            return redirect("prontuarios")
    else:
        form = ClinicalRecordForm()
    return render(request, "core/prontuario_form.html", {"form": form})

@admin_required
def administracao(request):
    return render(request, "core/administracao.html", {
        "templates": AttendanceTemplate.objects.filter(is_deleted=False),
        "rooms": Room.objects.all(),
        "specialties": Specialty.objects.all(),
    })

@admin_required
def modelo_documento_novo(request):
    if request.method == "POST":
        form = AttendanceTemplateForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_event(request.user, "Modelo criado", obj, "Modelo de declaração criado.")
            messages.success(request, "Modelo criado.")
            return redirect("administracao")
    else:
        form = AttendanceTemplateForm()
    return render(request, "core/modelo_form.html", {"form": form, "title": "Novo modelo de comparecimento"})

@admin_required
def modelo_documento_editar(request, pk):
    obj = get_object_or_404(AttendanceTemplate, pk=pk, is_deleted=False)
    if request.method == "POST":
        form = AttendanceTemplateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            log_event(request.user, "Modelo editado", obj, "Modelo de declaração editado.")
            messages.success(request, "Modelo atualizado.")
            return redirect("administracao")
    else:
        form = AttendanceTemplateForm(instance=obj)
    return render(request, "core/modelo_form.html", {"form": form, "title": "Editar modelo"})

@admin_required
@require_POST
def modelo_documento_alternar(request, pk):
    obj = get_object_or_404(AttendanceTemplate, pk=pk, is_deleted=False)
    obj.active = not obj.active
    obj.save(update_fields=["active", "updated_at"])
    log_event(request.user, "Modelo ativado/desativado", obj, "Situação do modelo alterada.")
    messages.success(request, "Situação do modelo atualizada.")
    return redirect("administracao")

@admin_required
@require_POST
def modelo_documento_excluir(request, pk):
    obj = get_object_or_404(AttendanceTemplate, pk=pk, is_deleted=False)
    obj.is_deleted = True
    obj.active = False
    obj.save(update_fields=["is_deleted", "active", "updated_at"])
    log_event(request.user, "Modelo excluído", obj, "Modelo removido da lista; declarações já emitidas foram preservadas.")
    messages.success(request, "Modelo removido. Declarações emitidas anteriormente foram preservadas.")
    return redirect("administracao")

@admin_required
def especialidades_admin(request):
    return render(request, "core/especialidades_admin.html", {"specialties": Specialty.objects.all()})

@admin_required
def especialidade_nova(request):
    if request.method == "POST":
        form = SpecialtyForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_event(request.user, "Especialidade criada", obj, "Especialidade cadastrada.")
            messages.success(request, "Especialidade cadastrada.")
            return redirect("especialidades_admin")
    else:
        form = SpecialtyForm()
    return render(request, "core/simple_form.html", {"form": form, "title": "Nova especialidade", "back_url": "especialidades_admin"})

@admin_required
def salas_admin(request):
    return render(request, "core/salas_admin.html", {"rooms": Room.objects.all()})

@admin_required
def sala_nova(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_event(request.user, "Sala criada", obj, "Sala cadastrada.")
            messages.success(request, "Sala cadastrada.")
            return redirect("salas_admin")
    else:
        form = RoomForm()
    return render(request, "core/simple_form.html", {"form": form, "title": "Nova sala", "back_url": "salas_admin"})

@admin_required
def auditoria(request):
    events = AuditEvent.objects.select_related("user")[:300]
    return render(request, "core/auditoria.html", {"events": events})
