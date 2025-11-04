from rest_framework import generics
from competitions.models import Submission
from competitions.serializers import SubmissionScoreSerializer

# Class for updating a score as an Admin
class ScoreUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionScoreSerializer
