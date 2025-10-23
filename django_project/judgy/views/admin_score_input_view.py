from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from ..models import Submission, Competition
from ..serializers import SubmissionScoreSerializer

# Class for updating a score as an Admin
class ScoreUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionScoreSerializer
