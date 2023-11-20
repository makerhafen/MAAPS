from datetime import timedelta

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session, get_profile_from_url_token
import maaps.models as models
from django.utils import timezone
from django.db.models import Q

def _get_price(profile, identifier):
    price = models.Price.objects.get(identifier = identifier)
    if profile.get_paying_user().commercial_account:
        return price.commercial
    elif profile.get_paying_user().discount_account:
        return price.discount
    elif profile.get_paying_user().monthly_payment:
        return price.members
    else:
        return price.default

def pos__login_user(request, user_token=""):
    profile, error = get_profile_from_post(request)
    if profile is None and user_token != "":
        profile, error = get_profile_from_url_token(user_token)

    if profile is not None:
        paying_user = profile.user
        if profile.paying_user is not None:
            paying_user = profile.paying_user

        if paying_user.profile.monthly_payment is True:
            try:
                current_spaceRentPayment = models.SpaceRentPayment.objects.filter(for_user=profile.user, user=paying_user, start__lt = timezone.now(), end__gt = timezone.now())[0]
            except:
                current_spaceRentPayment = None
        else:
            try:
                current_spaceRentPayment = models.SpaceRentPayment.objects.filter(for_user=profile.user, user=paying_user, end__gt=timezone.now())[0]
            except:
                current_spaceRentPayment = None
            if current_spaceRentPayment is not None: # benuzer ist anwesend
                pass
                #spaceAccessTracking.spaceRentPayment = current_spaceRentPayment
                #spaceAccessTracking.save()
            else:
                spaceRentPayment = models.SpaceRentPayment()
                spaceRentPayment.start = timezone.now() # spaceAccessTracking.start
                spaceRentPayment.end = spaceRentPayment.start + timedelta(hours=24)
                spaceRentPayment.user = paying_user
                spaceRentPayment.for_user = profile.user
                spaceRentPayment.price = _get_price(paying_user.profile, identifier="spaceRentPayment.daily")
                spaceRentPayment.type = models.SpaceRentPaymentType.daily
                spaceRentPayment.save()
                if paying_user.profile.allow_postpaid is False:
                    transaction = models.Transaction()
                    transaction.user = paying_user
                    transaction.value = spaceRentPayment.price
                    transaction.type = models.TransactionType.from_deposit_for_rent
                    transaction.save()
                    paying_user.profile.prepaid_deposit -= transaction.value
                    paying_user.profile.save()
                    spaceRentPayment.transaction = transaction
                    spaceRentPayment.save()
                #spaceAccessTracking.spaceRentPayment = spaceRentPayment
                #spaceAccessTracking.save()
    #else:
    #    return redirect('pos__index')

    template = loader.get_template('pos/login_user.html')
    return HttpResponse(template.render({
        "profile": profile,
        "last_error": error
    }, request))
