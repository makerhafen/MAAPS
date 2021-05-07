from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session


def pos__index(request):
    admin_profile = get_profile_from_session(request)
    error = None
    template = loader.get_template('pos/index.html')
    return HttpResponse(template.render({
        "admin_profile": admin_profile,
        "last_error": error
    }, request))
