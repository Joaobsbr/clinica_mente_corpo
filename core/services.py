from datetime import datetime, timedelta
from .models import Appointment, AuditEvent

def log_event(user, action, obj, summary):
    AuditEvent.objects.create(
        user=user,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=str(obj.pk),
        summary=summary[:255],
    )

def appointment_conflict(appointment):
    start = appointment.start_time
    end = appointment.end_time
    if not end:
        end = (datetime.combine(appointment.appointment_date, start) + timedelta(minutes=50)).time()
        appointment.end_time = end

    active_status = ["scheduled", "confirmed", "waiting"]
    base = Appointment.objects.filter(
        appointment_date=appointment.appointment_date,
        status__in=active_status,
        start_time__lt=end,
        end_time__gt=start,
    ).exclude(pk=appointment.pk)

    if base.filter(professional=appointment.professional).exists():
        return "Este profissional já possui atendimento nesse intervalo."
    if appointment.room_id and base.filter(room=appointment.room).exists():
        return "Esta sala já está ocupada nesse intervalo."
    if base.filter(patient=appointment.patient).exists():
        return "Este paciente já possui outro agendamento nesse intervalo."
    return None

def render_attendance_text(template_body, appointment, clinic_name, clinic_address):
    patient = appointment.patient
    weekday_pt = [
        "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"
    ][appointment.appointment_date.weekday()]
    replacements = {
        "{{ paciente }}": patient.full_name,
        "{{ data }}": appointment.appointment_date.strftime("%d/%m/%Y"),
        "{{ dia_semana }}": weekday_pt,
        "{{ hora_inicio }}": appointment.start_time.strftime("%H:%M"),
        "{{ hora_fim }}": appointment.end_time.strftime("%H:%M") if appointment.end_time else "",
        "{{ profissional }}": appointment.professional.get_full_name() or appointment.professional.username,
        "{{ servico }}": appointment.specialty.name,
        "{{ clinica }}": clinic_name,
        "{{ endereco }}": clinic_address,
    }
    text = template_body
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text
