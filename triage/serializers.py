from rest_framework import serializers
from .models import AIFinding


class AIFindingSerializer(serializers.ModelSerializer): #auto-generates fields by inspecting the AIFinding model
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0) #overrides the auto-generated confidence field and binds its values

    class Meta:
        model = AIFinding #Which model to build fields from and save to
        fields = ["id", "study", "label", "confidence", "critical", "review_status"] #whitelists which columns get exposed in JSON both in and out
                                                                                     # explicit listing instead of "__all__" in case of model changes later
