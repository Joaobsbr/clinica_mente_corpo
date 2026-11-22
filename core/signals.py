from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ProfessionalProfile

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_professional_profile(sender, instance, created, **kwargs):
    if created:
        ProfessionalProfile.objects.get_or_create(
            user=instance,
            defaults={
                "role": ProfessionalProfile.ROLE_ADMIN if instance.is_superuser else ProfessionalProfile.ROLE_BASIC,
                "is_professional": not instance.is_superuser,
                "can_access_records": instance.is_superuser,
            },
        )
    elif hasattr(instance, "professional_profile"):
        profile = instance.professional_profile
        if instance.is_superuser and profile.role != ProfessionalProfile.ROLE_ADMIN:
            profile.role = ProfessionalProfile.ROLE_ADMIN
            profile.save(update_fields=["role"])
