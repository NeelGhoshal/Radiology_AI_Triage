from rest_framework import serializers
from .models import AIFinding


class AIFindingSerializer(serializers.ModelSerializer): #auto-generates fields by inspecting the AIFinding model
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0) #overrides the auto-generated confidence field and binds its values

    #read-only study details, so a worklist row can be shown without a second request per study
    accession_id = serializers.CharField(source="study.accession_id", read_only=True)
    modality = serializers.CharField(source="study.modality", read_only=True)
    body_part = serializers.CharField(source="study.body_part", read_only=True)
    received_at = serializers.DateTimeField(source="study.received_at", read_only=True)

    class Meta:
        model = AIFinding #Which model to build fields from and save to
        fields = [
            "id", "study", "accession_id", "modality", "body_part", "received_at",
            "label", "confidence", "critical", "review_status",
        ] #whitelists which columns get exposed in JSON both in and out
                                                                                     # explicit listing instead of "__all__" in case of model changes later
