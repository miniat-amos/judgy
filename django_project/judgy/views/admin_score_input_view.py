from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Submission
from ..serializers import CompSerializer

# Class for updating a competition
class ScoreUpdate(APIView):
    def put(self, request, submission):
        
        
        competition = get_object_or_404(Competition, code=code)
        
        serializer = CompSerializer(competition, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            redirect_url = reverse("judgy:competition_code", kwargs={"code":code})
            return Response({"success": f"Competition {competition.name} updated successfully!", "redirect_url": redirect_url}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
