from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_session

def pos__logout_staff(request):
    admin_profile = get_profile_from_session(request)
    if admin_profile is not None:
        request.session["profile_id"] = None
    return redirect('pos__index')
