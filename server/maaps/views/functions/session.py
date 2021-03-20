from django.shortcuts import redirect
import maaps.models as models

def find_session_redirect(machine):
    if machine is None:
        return redirect('machine__login')
    if machine.currentSession is None:
        return redirect('machine__login_user')
    if machine.currentSession.tutor == None and machine.user_requires_tutor(machine.currentSession.user):
        return redirect('machine__tutor_required')
    if machine.currentSession.tutor == None and machine.user_requires_tutor_once(machine.currentSession.user):
        return redirect('machine__tutor_required')
    if machine.currentSession.rating_clean == -1 and machine.ask_clean is True:
        return redirect('machine__rate_machine')
    if (machine.price_per_hour > 0 or machine.currentSession.machine.price_per_usage > 0) and hasattr(machine.currentSession, "paymentsession") == False:
        return redirect('machine__payment_required')
    return redirect('machine__show_session')

def get_machine_from_session(request):
    machine_id = request.session.get("machine_id", None)
    machine = None
    if machine_id is not None:
        try:
            machine = models.Machine.objects.get(pk=machine_id)
        except:
            pass
    return machine

def get_profile_from_session(request):
    profile_id = request.session.get("profile_id", None)
    profile = None
    if profile_id is not None:
        try:
            profile = models.Profile.objects.get(pk=profile_id)
        except:
            pass
    return profile

def get_token_from_post(request):
    if request.method != "POST":
        return None, None
    rfid_token = request.POST.get("rfid_token", None)
    if rfid_token is None:
        return None, "no_token_posted"
    if rfid_token == "":
        return None, "empty_token"
    if "\t" not in rfid_token:
        return None, "invalid_token"

    id, rfid_token = rfid_token.split('\t')
    try:
        obj = models.Token.objects.get(identifier=rfid_token)
        return obj, ""
    except Exception as e:
        return None, "unknown_token"

def get_machine_from_post(request):
    token, lasterror = get_token_from_post(request)
    obj = None
    if token is not None:
        if token.machine is not None:
            obj = token.machine
            request.session["machine_id"] = token.machine.id
        else:
            lasterror ="no_machine_token"
    return obj, lasterror

def get_profile_from_post(request):
    token, lasterror = get_token_from_post(request)
    obj = None
    if token is not None:
        if token.profile is not None:
            obj = token.profile
        else:
            lasterror = "no_user_token"
    return obj, lasterror
