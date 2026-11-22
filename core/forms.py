from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Patient, Appointment, Room, Specialty, ProfessionalAvailability,
    ProfessionalProfile, AttendanceTemplate, ClinicalRecord
)

User = get_user_model()

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "full_name", "birth_date", "sex", "cpf", "no_cpf", "phone", "email",
            "self_guardian", "guardian_name", "guardian_age", "guardian_birth_date",
            "guardian_relationship", "guardian_profession", "street", "neighborhood",
            "status", "notes",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "guardian_birth_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        data = super().clean()
        if data.get("no_cpf"):
            data["cpf"] = ""
        if data.get("self_guardian"):
            data["guardian_name"] = ""
            data["guardian_age"] = None
            data["guardian_birth_date"] = None
            data["guardian_relationship"] = ""
            data["guardian_profession"] = ""
        elif not data.get("guardian_name"):
            self.add_error("guardian_name", "Informe o nome do responsável ou marque que o próprio paciente é o responsável.")
        return data


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "professional", "specialty", "appointment_date", "start_time", "end_time", "modality", "room", "observation"]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "observation": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.filter(status="active").order_by("full_name")
        # Usuários Básicos podem agendar pacientes com qualquer profissional
        # ativo; o nível de acesso limita módulos administrativos, não a escolha
        # do profissional que realizará o atendimento.
        professionals = User.objects.filter(
            is_active=True, professional_profile__is_professional=True
        ).order_by("first_name", "username")
        self.fields["professional"].queryset = professionals
        self.fields["specialty"].queryset = Specialty.objects.filter(active=True).order_by("name")
        self.fields["room"].queryset = Room.objects.filter(active=True).order_by("name")

    def clean(self):
        data = super().clean()
        start, end = data.get("start_time"), data.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "O horário final deve ser posterior ao horário inicial.")
        return data


class ProfessionalCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150, required=False)
    email = forms.EmailField(label="E-mail")
    role = forms.ChoiceField(label="Nível de acesso", choices=ProfessionalProfile.ROLE_CHOICES)
    specialty = forms.ModelChoiceField(label="Especialidade", queryset=Specialty.objects.none(), required=False)
    registration = forms.CharField(label="Registro profissional", required=False)
    is_professional = forms.BooleanField(label="Pode receber agendamentos", required=False, initial=True)
    can_access_records = forms.BooleanField(label="Autorizado a acessar prontuários", required=False)
    show_on_site = forms.BooleanField(label="Exibir no site público", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["specialty"].queryset = Specialty.objects.filter(active=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, _ = ProfessionalProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data["role"]
            profile.specialty = self.cleaned_data.get("specialty")
            profile.registration = self.cleaned_data.get("registration", "")
            profile.is_professional = self.cleaned_data.get("is_professional", False)
            profile.can_access_records = self.cleaned_data.get("can_access_records", False)
            profile.show_on_site = self.cleaned_data.get("show_on_site", False)
            profile.save()
        return user


class ProfessionalEditForm(forms.Form):
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150, required=False)
    email = forms.EmailField(label="E-mail")
    role = forms.ChoiceField(label="Nível de acesso", choices=ProfessionalProfile.ROLE_CHOICES)
    specialty = forms.ModelChoiceField(label="Especialidade", queryset=Specialty.objects.none(), required=False)
    registration = forms.CharField(label="Registro profissional", required=False)
    is_professional = forms.BooleanField(label="Pode receber agendamentos", required=False)
    can_access_records = forms.BooleanField(label="Autorizado a acessar prontuários", required=False)
    show_on_site = forms.BooleanField(label="Exibir no site público", required=False)
    is_active = forms.BooleanField(label="Conta ativa", required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["specialty"].queryset = Specialty.objects.filter(active=True)
        if user:
            p = user.professional_profile
            self.initial.update({
                "first_name": user.first_name, "last_name": user.last_name, "email": user.email,
                "role": p.role, "specialty": p.specialty_id, "registration": p.registration,
                "is_professional": p.is_professional, "can_access_records": p.can_access_records,
                "show_on_site": p.show_on_site, "is_active": user.is_active,
            })

    def save(self):
        user = self.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.is_active = self.cleaned_data.get("is_active", False)
        user.save()
        p = user.professional_profile
        p.role = self.cleaned_data["role"]
        p.specialty = self.cleaned_data.get("specialty")
        p.registration = self.cleaned_data.get("registration", "")
        p.is_professional = self.cleaned_data.get("is_professional", False)
        p.can_access_records = self.cleaned_data.get("can_access_records", False)
        p.show_on_site = self.cleaned_data.get("show_on_site", False)
        p.save()
        return user


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = ProfessionalAvailability
        fields = ["professional", "weekday", "start_time", "end_time", "modality", "room"]
        widgets = {"start_time": forms.TimeInput(attrs={"type": "time"}), "end_time": forms.TimeInput(attrs={"type": "time"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["professional"].queryset = User.objects.filter(is_active=True, professional_profile__is_professional=True)
        self.fields["room"].queryset = Room.objects.filter(active=True)
        if user and not (user.is_superuser or user.professional_profile.role == ProfessionalProfile.ROLE_ADMIN):
            self.fields["professional"].queryset = self.fields["professional"].queryset.filter(pk=user.pk)
            self.initial["professional"] = user.pk

    def clean(self):
        data = super().clean()
        if data.get("start_time") and data.get("end_time") and data["end_time"] <= data["start_time"]:
            self.add_error("end_time", "O horário final deve ser posterior ao início.")
        return data


class AttendanceTemplateForm(forms.ModelForm):
    class Meta:
        model = AttendanceTemplate
        fields = ["name", "body", "active"]
        widgets = {"body": forms.Textarea(attrs={"rows": 8})}


class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ["name", "description", "active", "public_on_site"]


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "active"]


class ClinicalRecordForm(forms.ModelForm):
    class Meta:
        model = ClinicalRecord
        fields = ["patient", "appointment", "content"]
        widgets = {"content": forms.Textarea(attrs={"rows": 8})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.filter(status="active")
        self.fields["appointment"].queryset = Appointment.objects.all()
