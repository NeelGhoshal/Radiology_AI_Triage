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