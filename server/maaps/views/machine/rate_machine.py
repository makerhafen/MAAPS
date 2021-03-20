from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, find_session_redirect


def machine__rate_machine(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    clean_rating = request.POST.get("clean_rating", None)
    if clean_rating is not None:
        try:
            clean_rating = int(clean_rating)
            if clean_rating > 0 and clean_rating < 6:
                machine.currentSession.rating_clean = clean_rating
                machine.currentSession.save()
                return find_session_redirect(machine)
        except Exception as e:
            print("Failed to save rating:", e)

    return HttpResponse(loader.get_template('machine/rate_machine.html').render({
        "machine": machine
    }, request))