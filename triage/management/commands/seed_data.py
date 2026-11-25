import random
from django.core.management.base import BaseCommand
from triage.models import Study, AIFinding

#label: (modalities, body parts) it can plausibly show up on, so the fake data makes anatomical sense
FINDINGS = {
    "Pneumothorax": (["XR", "CT"], ["Chest"]),
    "Pulmonary nodule": (["XR", "CT"], ["Chest"]),
    "Cardiomegaly": (["XR", "CT", "MR"], ["Chest"]),
    "Fracture": (["XR", "CT", "MR"], ["Spine", "Pelvis"]),
    "Hemorrhage": (["CT", "MR"], ["Head", "Abdomen", "Pelvis"]),
}


class Command(BaseCommand):
    help = "Seed the database with made-up studies and AI findings for testing."

    def add_arguments(self, parser): #parser is an argument parser which can be used later in this function
        parser.add_argument("--count", type=int, default=20) #count defines how many counts of rows of data to seed
        #eg: python manage.py seed_data --count 50 adds 50 rows
        parser.add_argument("--reviewed", type=int, default=0, help="How many of the new findings to mark as already reviewed.")
        parser.add_argument("--if-empty", action="store_true", help="Do nothing if the database already has studies.")

    def handle(self, *args, **options):
        if options["if_empty"] and Study.objects.exists():
            self.stdout.write("Database already has studies, nothing seeded.")
            return

        count = options["count"] #Pulls number out into a plain variable
        reviewed = min(options["reviewed"], count)
        taken = set(Study.objects.values_list("accession_id", flat=True)) #accession_id is unique, so never reuse one

        for i in range(count): #Data creation
            accession_id = f"ACC-{random.randint(10000, 99999)}"
            while accession_id in taken:
                accession_id = f"ACC-{random.randint(10000, 99999)}"
            taken.add(accession_id)

            confidence = round(random.uniform(0.5, 0.99), 2)
            review_status = "pending"
            if i < reviewed: #the more confident the AI was, the likelier the made-up radiologist agrees
                review_status = "confirmed" if random.random() < confidence else "rejected"

            label = random.choice(list(FINDINGS))
            modalities, body_parts = FINDINGS[label]
            study = Study.objects.create(
                accession_id=accession_id,
                modality=random.choice(modalities),
                body_part=random.choice(body_parts),
            )
            AIFinding.objects.create(
                study=study,
                label=label,
                confidence=confidence,
                critical=random.choice([True, False]),
                review_status=review_status,
            )

        self.stdout.write(self.style.SUCCESS(f"Created {count} studies with findings."))
