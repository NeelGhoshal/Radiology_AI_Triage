from django.urls import path
from .views import WorklistView

urlpatterns = [
    path("worklist/", WorklistView.as_view(), name="worklist"), #.as_view() converts the class into callable Django requeest router
] #mounted to config urls.py under findings