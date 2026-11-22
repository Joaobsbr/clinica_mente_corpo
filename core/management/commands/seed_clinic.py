from django.core.management.base import BaseCommand
from core.models import Specialty, AttendanceTemplate

SPECIALTIES = [
    ("Fisioterapia", "Prevenção e reabilitação do movimento."),
    ("Estética", "Cuidados estéticos e bem-estar."),
    ("Psicologia", "Atenção à saúde emocional."),
    ("Clínico", "Atendimento clínico."),
    ("Nutrição", "Orientação nutricional."),
    ("Fonoaudiologia", "Comunicação, linguagem e audição."),
    ("Psicopedagogia", "Acompanhamento da aprendizagem."),
    ("Neuropsicopedagogia", "Desenvolvimento e aprendizagem."),
    ("Pneumologista", "Atenção à saúde respiratória."),
    ("Saúde do Adolescente", "Acompanhamento integral do adolescente."),
]

DEFAULT_TEMPLATE = """DECLARAÇÃO DE COMPARECIMENTO

Declaramos, para os devidos fins, que {{ paciente }} compareceu ao {{ clinica }}, localizado em {{ endereco }}, no dia {{ data }}, das {{ hora_inicio }} às {{ hora_fim }}, para atendimento de {{ servico }}.

Documento emitido em {{ data }}.
"""

class Command(BaseCommand):
    help = "Cria especialidades iniciais e modelo padrão de declaração."

    def handle(self, *args, **options):
        for name, description in SPECIALTIES:
            Specialty.objects.get_or_create(name=name, defaults={"description": description, "public_on_site": True})
        AttendanceTemplate.objects.get_or_create(
            name="Declaração padrão de comparecimento",
            is_deleted=False,
            defaults={"body": DEFAULT_TEMPLATE, "active": True},
        )
        self.stdout.write(self.style.SUCCESS("Especialidades e modelo inicial preparados."))
