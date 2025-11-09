from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render

from competition.models import Competition, Problem, Submission, Team


@user_passes_test(lambda u: u.is_superuser)
def admin_problem_submissions(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)

    team_filter = request.GET.get("team", "").strip()
    order = request.GET.get("order", "latest")

    submissions = (
        Submission.objects.filter(problem=problem)
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
        "problem": problem,
        "submissions": submissions,
        "team_filter": team_filter,
        "order": order,
        "teams": teams,
        "submission_count": submissions.count(),
    }

    return render(
        request, "judgy/admin_problem_submissions.html", context=context
    )
