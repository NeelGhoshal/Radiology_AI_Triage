from django.contrib import admin
from .models import Study, AIFinding


@admin.register(Study) #To register the model
class StudyAdmin(admin.ModelAdmin):
    list_display = ("accession_id", "modality", "body_part", "received_at") #which columns show up in the table view


@admin.register(AIFinding)
class AIFindingAdmin(admin.ModelAdmin):
    list_display = ("study", "label", "confidence", "critical", "review_status")
    list_filter = ("review_status", "critical") #adds a sidebar to filter the list 
