from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session

def pos__index(request):
    admin_profile = get_profile_from_session(request)
    error = None
    if admin_profile is None:
        profile, error = get_profile_from_post(request)
        if profile is not None:
            if profile.user.is_staff:
                request.session["profile_id"] = profile.id
                admin_profile = profile
            else:
                error = "user_is_not_staff"

    template = loader.get_template('pos/index.html')
    return HttpResponse(template.render({
        "admin_profile": admin_profile,
        "last_error": error
    }, request))

def pos__logout(request):
    admin_profile = get_profile_from_session(request)
    if admin_profile is not None:
        request.session["profile_id"] = None
        admin_profile = None
    return redirect('pos__index')

