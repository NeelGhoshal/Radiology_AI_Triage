from django.urls import path
from .views import WorklistView, ReviewFindingView, StatsView

urlpatterns = [
    path("worklist/", WorklistView.as_view(), name="worklist"), #.as_view() converts the class into callable Django requeest router
    path("<int:pk>/review/", ReviewFindingView.as_view(), name="review-finding"),
    path("stats/", StatsView.as_view(), name="stats"),
] #mounted to config urls.py under findings