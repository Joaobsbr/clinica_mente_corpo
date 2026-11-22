from django.contrib import admin
from .models import (
    Patient, Appointment, Room, Specialty, ProfessionalProfile,
    ProfessionalAvailability, AttendanceTemplate, AttendanceDeclaration,
    ClinicalRecord, AuditEvent
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "cpf", "status", "created_at")
    search_fields = ("full_name", "guardian_name", "cpf", "phone")
    list_filter = ("status", "sex", "no_cpf")

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("appointment_date", "start_time", "patient", "professional", "specialty", "room", "status")
    list_filter = ("appointment_date", "status", "specialty", "professional", "modality")
    search_fields = ("patient__full_name", "patient__guardian_name", "professional__username")

admin.site.register(ProfessionalProfile)
admin.site.register(Room)
admin.site.register(Specialty)
admin.site.register(ProfessionalAvailability)
admin.site.register(AttendanceTemplate)
admin.site.register(AttendanceDeclaration)
admin.site.register(ClinicalRecord)
admin.site.register(AuditEvent)
