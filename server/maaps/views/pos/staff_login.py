from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session, get_profile_from_url_token


def pos__staff_login(request, user_token=""):
    admin_profile = get_profile_from_session(request)
    error = None
    if admin_profile is None:
        profile, error = get_profile_from_post(request)
        if profile is None and user_token != "":
            profile, error = get_profile_from_url_token(user_token)

        if profile is not None:
            if profile.user.is_staff:
                request.session["profile_id"] = profile.id
                return redirect('pos__index')
            else:
                error = "user_is_not_staff"
    else:
        return redirect('pos__index')

    template = loader.get_template('pos/staff_login.html')
    return HttpResponse(template.render({
        "admin_profile": admin_profile,
        "last_error": error
    }, request))
