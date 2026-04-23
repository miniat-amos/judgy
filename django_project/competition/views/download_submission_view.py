import os
import zipfile
from django.http import HttpResponse
from competition.utils import get_user_submission_dir
from django.contrib.auth.decorators import user_passes_test
from competition.utils import create_formatted_name

@user_passes_test(lambda u: u.is_superuser)
def download_submission_view(request, code, problem_name, team_name, email, submission_id):
        submission_dir = get_user_submission_dir(code, team_name, email, problem_name, submission_id)

        submission_zip = f'/tmp/{email}.zip'

        # Create a zip file
        with zipfile.ZipFile(submission_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(submission_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, submission_dir))

        # Read the zip file and return it in an HTTP response
        with open(submission_zip, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            # Set the Content-Disposition header to prompt the user to download the file
            
            name_vars = [email.split('@')[0], problem_name.replace(" ", "_"), submission_id, ".zip"]
            formatted_name = create_formatted_name(name_vars, "_")
            response['Content-Disposition'] = f'attachment; filename="{formatted_name}"'

        os.remove(submission_zip)

        return response
