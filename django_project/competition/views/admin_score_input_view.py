from rest_framework import generics
from competition.models import Submission
from competition.serializers import SubmissionScoreSerializer
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
        self.perform_update(serializer)

        user = instance.user
        score = instance.score
        problem_name = instance.problem.name
        competition_name = instance.problem.competition.name
        body=f'You got a score of {score} in the problem "{problem_name}" for the competition "{competition_name}".'


        # Create your notification
        Notification.objects.create(
            user=user,
            header="Your Score",
            body=body
        )

        return Response(serializer.data)

