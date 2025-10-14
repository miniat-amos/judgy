import os
import zipfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Competition
from ..utils import get_dist_dir

def download_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)

    if competition.start <= timezone.now():
        dist_dir = get_dist_dir(code, problem_name)

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
            response['Content-Disposition'] = f'attachment; filename="{problem_name}.zip"'

        os.remove(problem_zip)

        return response
