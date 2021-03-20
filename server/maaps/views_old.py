from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from . import models
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Q




# machine/session/auto_logout
def machine__session__auto_logout__index(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    return HttpResponse(loader.get_template('machine/session/auto_logout/index.html').render({
        "machine": machine
    }, request))

# machine/session/auto_logout/clock
def machine__session__auto_logout__clock(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    template = loader.get_template('machine/session/auto_logout/clock.html')
    return HttpResponse(template.render({
        "machine": machine
    }, request))

# machine/session/auto_logout/timer
def machine__session__auto_logout__timer(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    template = loader.get_template('machine/session/auto_logout/timer.html')
    return HttpResponse(template.render({
        "machine": machine
    }, request))












