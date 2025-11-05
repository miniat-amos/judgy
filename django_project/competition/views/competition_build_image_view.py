from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from ..tasks import create_images_task


@user_passes_test(lambda u: u.is_superuser)
def build_image(request, code):
   if request.method == "POST":
       try:
           result = create_images_task.delay(code)
           return JsonResponse({"status": "started", "task_id": result.id}, status=200)
       except Exception as e:
           return JsonResponse({"error": str(e)}, status=500)
   else:
       return JsonResponse({"error": "Invalid request"}, status=400)