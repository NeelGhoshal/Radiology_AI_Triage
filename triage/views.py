from rest_framework.generics import ListAPIView
from .models import AIFinding
from .serializers import AIFindingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q


class WorklistView(ListAPIView): #WorkList to be displayed to doctors to sign off on ranked according to critical and confidence metrics
    serializer_class = AIFindingSerializer #links to serializer shaping each AIFindning into JSON
    queryset = AIFinding.objects.filter(review_status="pending").order_by( #only findings no-one has reviewed yet
        "-critical", "-confidence" #- prefix means descending, Critical Trues would come before False
    )

class ReviewFindingView(APIView): #To let the radiologist submit their verdict on specific AI Findings
    def post(self, request, pk): #method for calling POST #self is the view instance, incoming request (body, headers), pk: numeric ID captured from the URL
        finding = get_object_or_404(AIFinding, pk=pk) #looks up AIFinding row with that primary key, instance assigned
                                                      #or 404 helps return the error, alternate is try/except
        if finding.review_status != "pending":
            return Response(
                {"error": "This finding has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = request.data.get("status")
        if new_status not in ("confirmed", "rejected"):
            return Response(
                {"error": "status must be 'confirmed' or 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        finding.review_status = new_status
        finding.save()

        return Response(AIFindingSerializer(finding).data, status=status.HTTP_200_OK)

class StatsView(APIView): #To turn individual review decisions into a measurable track record (fraction of AI's flags do radiologists actually confirm)
    def get(self, request): #get maps the method to GET 
        queryset = AIFinding.objects.all() #Get all rows

        modality = request.query_params.get("modality") #Get modality from request like /findings/stats/?modality=XR
        if modality:
            queryset = queryset.filter(study__modality=modality) #filters by traversing the ForeignKet from AIFinding to its related study and filters by the studiy's modality

        counts = queryset.aggregate( #runs a query which computes 2 conditional counts at once
            reviewed=Count("id", filter=~Q(review_status="pending")), #The count of rows where review_status is not pending
            confirmed=Count("id", filter=Q(review_status="confirmed")), #The count of rows where review_status is confirmed
        )
        reviewed = counts["reviewed"]
        confirmed = counts["confirmed"]
        rate = confirmed / reviewed if reviewed else None #Computer rate con/rev but only if reviewed is nonzero, if review is 0 then return None

        return Response(
            {
                "modality": modality,
                "reviewed": reviewed,
                "confirmed": confirmed,
                "confirmation_rate": rate,
            }
        )