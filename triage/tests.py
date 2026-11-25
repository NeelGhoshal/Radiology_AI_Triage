from io import StringIO

from django.core.management import call_command
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Study, AIFinding


class ReviewFindingTests(APITestCase):
    def setUp(self):
        self.study = Study.objects.create(accession_id="ACC-1", modality="XR", body_part="Chest")
        self.finding = AIFinding.objects.create(study=self.study, label="Test", confidence=0.9)

    def test_review_confirms_pending_finding(self):
        response = self.client.post(f"/findings/{self.finding.id}/review/", {"status": "confirmed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_double_review_returns_400(self):
        self.client.post(f"/findings/{self.finding.id}/review/", {"status": "confirmed"}, format="json")
        response = self.client.post(f"/findings/{self.finding.id}/review/", {"status": "rejected"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_id_returns_404(self):
        response = self.client.post("/findings/99999/review/", {"status": "confirmed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FrontendTests(APITestCase):
    def test_home_page_loads_and_sets_csrf_cookie(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("csrftoken", response.cookies)

    def test_worklist_includes_study_details(self):
        study = Study.objects.create(accession_id="ACC-2", modality="CT", body_part="Head")
        AIFinding.objects.create(study=study, label="Hemorrhage", confidence=0.8, critical=True)
        finding = self.client.get("/findings/worklist/").json()[0]
        self.assertEqual(finding["accession_id"], "ACC-2")
        self.assertEqual(finding["modality"], "CT")
        self.assertEqual(finding["body_part"], "Head")


class SeedDataTests(APITestCase):
    def test_reviewed_findings_are_seeded(self):
        call_command("seed_data", "--count", "10", "--reviewed", "4", stdout=StringIO())
        self.assertEqual(AIFinding.objects.count(), 10)
        self.assertEqual(AIFinding.objects.exclude(review_status="pending").count(), 4)

    def test_if_empty_does_not_seed_twice(self):
        for _ in range(2):
            call_command("seed_data", "--count", "3", "--if-empty", stdout=StringIO())
        self.assertEqual(Study.objects.count(), 3)
