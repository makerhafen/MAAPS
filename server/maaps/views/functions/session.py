from django.shortcuts import redirect
import maaps.models as models
from django.utils import timezone


def find_session_redirect(machine):
    if machine is None:
        return redirect('machine__login')
    if machine.current_session is None:
        return redirect('machine__login_user')
    if machine.current_session.tutor is None and machine.user_requires_tutor(machine.current_session.user):
        # if machine.last_session.tutor is not None and machine.last_session.ended < 1h:
        #   machine.current_session.tutor = machine.last_session.tutor
        return redirect('machine__tutor_required')
    if machine.current_session.tutor is None and machine.user_requires_tutor_once(machine.current_session.user):
        return redirect('machine__tutor_required')
    if machine.current_session.rating_clean == -1 and machine.ask_clean is True:
        # and if machine.last_session.user != machine.current_session.user   # user has changed, ask
        return redirect('machine__rate_machine')
    paying_user_profile = machine.current_session.user.profile
    if paying_user_profile.paying_user is not None:
        paying_user_profile = paying_user_profile.paying_user.profile
    if machine.requires_payment(paying_user_profile) and hasattr( machine.current_session, "machineSessionPayment") == False:
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

    _id, rfid_token = rfid_token.split('\t')
    try:
        tkn = models.Token.objects.get(identifier=rfid_token)
        if tkn.enabled is False:
            return None, "token_disabled"
        return tkn, None
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
            lasterror = "no_machine_token"
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


def get_profile_from_url_token(token):
    if token is None:
        return None, "no_token_posted"
    if token == "":
        return None, "empty_token"
    if ";" not in token:
        return None, "invalid_token"

    try:
        tkn = models.Token.objects.get(identifier=token)
        if tkn.enabled is False:
            return None, "token_disabled"
        return tkn.profile, None
    except Exception as e:
        return None, "unknown_token"


def end_session(session):
    current_payment_session = None
    if session is not None:
        machine = session.machine
        if hasattr(session, "machineSessionPayment"):
            current_payment_session = session.machineSessionPayment
            current_payment_session.end = timezone.now()

            timediff_hours = (current_payment_session.end - current_payment_session.start).total_seconds() / 3600.0
            total_price = round(current_payment_session.price_per_usage + timediff_hours * current_payment_session.price_per_hour, 2)
            current_payment_session.price = total_price

            if current_payment_session.user.profile.allow_postpaid is False:
                transaction = models.Transaction()
                transaction.user = current_payment_session.user
                transaction.value = current_payment_session.price
                transaction.type = models.TransactionType.from_deposit_for_machine
                transaction.save()
                current_payment_session.transaction = transaction
                current_payment_session.user.profile.prepaid_deposit -= current_payment_session.price
                current_payment_session.user.profile.save()

            current_payment_session.save()
        if machine.current_session == session:
            machine.current_session = None
            machine.save()
        session.end = timezone.now()
        session.save()
        return session, current_payment_session
    return None, None