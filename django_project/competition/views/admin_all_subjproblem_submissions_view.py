from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render

from competition.models import Competition, Problem, Submission, Team


@user_passes_test(lambda u: u.is_superuser)
def admin_all_subjective_problem_submissions(request, code):
    competition = get_object_or_404(Competition, code=code)

    subjective_problems = Problem.objects.filter(
        competition=competition,
        subjective=True
    )

    team_filter = request.GET.get("team", "").strip()
    order = request.GET.get("order", "latest")

    submissions = (
        Submission.objects.filter(problem__in=subjective_problems)
        .select_related("team", "user")
    )

    if team_filter:
        submissions = submissions.filter(team__name=team_filter)

    if order == "earliest":
        submissions = submissions.order_by("time")
    else:
        order = "latest"
        submissions = submissions.order_by("-time")

    teams = Team.objects.filter(competition=competition).order_by("name")

    context = {
        "competition": competition,
        "problem": subjective_problems,
        "submissions": submissions,
        "team_filter": team_filter,
        "order": order,
        "teams": teams,
        "submission_count": submissions.count(),
    }

    return render(
        request, "judgy/admin_all_subjective_problems.html", context=context
    )
