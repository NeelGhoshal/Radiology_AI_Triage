import random
from django.core.management.base import BaseCommand
from triage.models import Study, AIFinding

MODALITIES = ["XR", "CT", "MR"]
BODY_PARTS = ["Chest", "Head", "Abdomen", "Pelvis", "Spine"]
LABELS = ["Pneumothorax", "Pulmonary nodule", "Fracture", "Hemorrhage", "Cardiomegaly"]


class Command(BaseCommand):
    help = "Seed the database with made-up studies and AI findings for testing."

    def add_arguments(self, parser): #parser is an argument parser which can be used later in this function
        parser.add_argument("--count", type=int, default=20) #count defines how many counts of rows of data to seed
        #eg: python manage.py seed_data --count 50 adds 50 rows

    def handle(self, *args, **options):
        count = options["count"] #Pulls number out into a plain variable

        for _ in range(count): #Data creation
            study = Study.objects.create(
                accession_id=f"ACC-{random.randint(10000, 99999)}",
                modality=random.choice(MODALITIES),
                body_part=random.choice(BODY_PARTS),
            )
            AIFinding.objects.create(
                study=study,
                label=random.choice(LABELS),
                confidence=round(random.uniform(0.5, 0.99), 2),
                critical=random.choice([True, False]),
            )

        self.stdout.write(self.style.SUCCESS(f"Created {count} studies with findings."))
