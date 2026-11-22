from .models import ProfessionalProfile

def clinic_context(request):
    if not request.user.is_authenticated:
        return {"user_profile": None, "is_clinic_admin": False, "can_access_clinical_records": False}
    try:
        profile = request.user.professional_profile
    except ProfessionalProfile.DoesNotExist:
        profile = None
    is_admin = bool(request.user.is_superuser or (profile and profile.role == ProfessionalProfile.ROLE_ADMIN))
    can_records = bool(is_admin or (profile and profile.can_access_records))
    return {"user_profile": profile, "is_clinic_admin": is_admin, "can_access_clinical_records": can_records}
