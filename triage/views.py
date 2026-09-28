from rest_framework.generics import ListAPIView
from .models import AIFinding
from .serializers import AIFindingSerializer


class WorklistView(ListAPIView): #WorkList to be displayed to doctors to sign off on ranked according to critical and confidence metrics
    serializer_class = AIFindingSerializer #links to serializer shaping each AIFindning into JSON
    queryset = AIFinding.objects.filter(review_status="pending").order_by( #only findings no-one has reviewed yet
        "-critical", "-confidence" #- prefix means descending, Critical Trues would come before False
    )
