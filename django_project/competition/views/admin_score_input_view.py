from rest_framework import generics
from competition.models import Submission
from competition.serializers import SubmissionScoreSerializer
from competition.utils import check_competition_best
from competition.models import Team
from notifications.models import Notification
from rest_framework.response import Response


# Class for updating a score as an Admin
class ScoreUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionScoreSerializer
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        
        user = instance.user
        new_score = serializer.validated_data.get('score', instance.score)
        problem = instance.problem
        competition = instance.problem.competition
        
        team = Team.objects.filter(competition=competition, members=user).first()
        
        check_competition_best(competition, problem, new_score, user, team) 
        
        self.perform_update(serializer)

        body=f'You got a score of {new_score} in the problem "{problem.name}" for the competition "{competition.name}".'

        # Create your notification
        Notification.objects.create(
            user=user,
            header="Your Score",
            body=body
        )
        

        return Response(serializer.data)

