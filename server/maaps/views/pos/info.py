from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_profile_from_post

def pos__info(request):
    user_profile, error = get_profile_from_post(request)
    template = loader.get_template('pos/info.html')
    return HttpResponse(template.render({
        "user_profile": user_profile,
        "last_error": error,
    }, request))
