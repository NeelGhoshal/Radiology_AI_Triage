from django.db import models


class Study(models.Model): #New Database model called Study, maps itself to a database table
                           # Table has a column for the fields defined below
                           # accession_id, modality, body_part, received_at are columns once migrations are run (as shown below)
#id	accession_id	modality	body_part	received_at
#1	ACC-48213	    XR	        Chest	    2026-09-27 14:03:00
#2	ACC-91027	    CT	        Head	    2026-09-27 14:05:12
    MODALITIES = [("XR", "X-ray"), ("CT", "CT"), ("MR", "MRI")] #Each tuple is (value_stored_in_db, label_shown_to_humans)
                                                                #XR gets written to the modality column (below) and X-ray is what a human sees (in dropdowns, generated forms, APIs)

    accession_id = models.CharField(max_length=20, unique=True) #doesn't allow repeated accession_ids
    modality = models.CharField(max_length=2, choices=MODALITIES) #limits choices to modalities list
    body_part = models.CharField(max_length=50)
    received_at = models.DateTimeField(auto_now_add=True) #never set manually and doesn't change after creation. unlike auto_now=True, which would update it on every save


class AIFinding(models.Model):
    study = models.ForeignKey( #like an order for a item, Foreign keys can have multiple entries relating to one of the study ids present
        Study, on_delete=models.CASCADE, related_name="findings" #Django adds a column called study_id to the AIFinding table.
                                                                 #CASCADE allows the auto removal of AI FIndings if study is deleted
                                                                 #findings helps to look up AI findings related to a study
    )
    label = models.CharField(max_length=100)
    confidence = models.FloatField()
    critical = models.BooleanField(default=False)
    review_status = models.CharField(
        max_length=10,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("rejected", "Rejected"),
        ],
    )
