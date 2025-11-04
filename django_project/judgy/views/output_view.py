from django.shortcuts import render, get_object_or_404
from judgy.decorators import verified_required
from judgy.models import Competition, Problem, Submission

@verified_required
def output_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)
    
    submissions = Submission.objects.filter(user=request.user, problem=problem).order_by('-time')

    outputs = [
        {
            'submission_time': s.time,
            'output_data': s.output,
            'file_name': s.file_name,
        }
        for s in submissions
    ]
    
    return render(request, 'judgy/submission_output.html', {
        'competition': competition,
        'problem': problem,
        'outputs': outputs
    })
