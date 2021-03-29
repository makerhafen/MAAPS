from maaps.views.functions.session import find_session_redirect

def machine__logout_machine(request):
    request.session["machine_id"] = None
    return find_session_redirect(None)
