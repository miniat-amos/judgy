from django.shortcuts import redirect
from functools import wraps

def verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('judgy:login')
        if not request.user.is_verified:
            return redirect('judgy:verify')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
