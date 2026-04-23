import os
import zipfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from competition.models import Competition
from competition.utils import get_problem_dir, create_formatted_name

def download_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)

    if competition.start <= timezone.now():
        
        problem_dir = get_problem_dir(code, problem_name)
        dist_dir = problem_dir / "dist"

        problem_zip = f'/tmp/{problem_name}.zip'

        # Create a zip file
        with zipfile.ZipFile(problem_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, dist_dir))

        # Read the zip file and return it in an HTTP response
        with open(problem_zip, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            # Set the Content-Disposition header to prompt the user to download the file
            name_vars = [problem_name.replace(' ', '_'), ".zip"]
            formatted_name = create_formatted_name(name_vars, "")
            response['Content-Disposition'] = f'attachment; filename="{formatted_name}"'

        os.remove(problem_zip)

        return response
