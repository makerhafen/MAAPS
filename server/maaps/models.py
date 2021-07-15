import itertools
import math
import os
import uuid
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django_resized import ResizedImageField
from django.utils import timezone


#
# HELPER FUNCTIONS
#
def rename_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}_{}.{}'.format(instance.user.username, now().strftime('%Y.%m.%d_%H.%M.%S'), ext)
    return os.path.join('photos/', filename)

#
# OTHER
#
class Price (models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    identifier = models.CharField(max_length=100, blank=True)
    discount = models.FloatField(default=0)
    default = models.FloatField(default=0)
    commercial = models.FloatField(default=0)

    def __str__(self):
        return "%s: %s, %s, %s" % (self.identifier, self.discount, self.default, self.commercial)

class Token(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    identifier = models.CharField(max_length=48, blank=True)
    enabled = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)  # true if terminal should show token to be written to rfid card
    profile = models.ForeignKey("Profile", related_name="tokens", on_delete=models.CASCADE, blank=True, null=True)
    machine = models.ForeignKey("Machine", related_name="tokens", on_delete=models.CASCADE, blank=True, null=True)

class SpaceAccessTracking(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spaceAccessTrackings", verbose_name='Benutzer')
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    spaceRentPayment = models.ForeignKey("SpaceRentPayment", on_delete=models.SET_NULL, blank=True, null=True, related_name="spaceAccessTrackings")


#
# ENUMS
#
class SpaceRentPaymentType:
    monthly = "monthly"
    daily = "daily"

class TransactionType:
    from_cash_for_deposit = "from_cash_for_deposit"
    from_cash_for_invoice = "from_cash_for_invoice"
    from_cash_for_rent = "from_cash_for_rent"
    from_bank_for_deposit = "from_bank_for_deposit"
    from_bank_for_invoice = "from_bank_for_invoice"
    from_bank_for_rent = "from_bank_for_rent"
    from_deposit_for_machine = "from_deposit_for_machine"
    from_deposit_for_material = "from_deposit_for_material"
    from_deposit_for_rent = "from_deposit_for_rent"

class InvoiceType:
    receipt = "receipt"
    invoice = "invoice"


#
# PROFILE
#
class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # USER DATA
    profile_picture = ResizedImageField(blank=True, null=True, upload_to=rename_file)
    birthdate = models.DateField(blank=True, null=True, default=None)
    company_name = models.CharField(max_length=200, blank=True, default="")

    #PAYMENT
    paying_user = models.ForeignKey("Profile", on_delete=models.CASCADE, blank=True, null=True)
    allow_postpaid = models.BooleanField(default=False)
    commercial_account = models.BooleanField(default=False)  # == mit mwst
    discount_account = models.BooleanField(default=False)  # z.b. < 16 Jahre
    monthly_payment = models.BooleanField(default=False)  # monatlich oder tagesaccount
    prepaid_deposit = models.FloatField(default=0)

    # ADDRESS
    street = models.CharField(max_length=200, blank=True, default="")
    postalcode = models.CharField(max_length=200, default="", blank=True)
    city = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        if self.company_name != "":
            return "%s, %s. %s" % (self.company_name, self.user.first_name[0].upper(), self.user.last_name)
        return "%s %s" % (self.user.first_name, self.user.last_name)

    def get_current_token(self):
        tokens = Token.objects.filter(enabled=True, profile=self)
        if len(tokens) == 0:
            return None
        return tokens[0]

    def is_underage(self):
        if self.birthdate is None:
            return False
        return timezone.now().date() - self.birthdate < timedelta(days=365*18)

    def get_paying_user(self):
        if self.paying_user is None:
            return self
        return self.paying_user


#
# MACHINE
#
class Machine(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    group_name = models.CharField(max_length=100, blank=True)
    comment = models.CharField(max_length=10000, blank=True)
    ask_clean = models.BooleanField(default=False)
    ask_pay_material = models.BooleanField(default=False)
    show_autologout = models.BooleanField(default=False)
    price_per_hour = models.ForeignKey(Price, on_delete=models.SET_NULL, related_name="machinePerHour", blank=True, null=True)  # in Euro
    price_per_usage = models.ForeignKey(Price, on_delete=models.SET_NULL, related_name="machinePerUsage", blank=True, null=True)  # in Euro
    tutor_required_count = models.IntegerField(default=0)  # wir oft
    tutor_required_once_after_month = models.IntegerField(default=24)  # all
    current_session = models.OneToOneField("MachineSession", on_delete=models.SET_NULL, related_name="current_session", blank=True, null=True)
    allowed_users = models.ManyToManyField(User, related_name="allowed_machines")

    def __str__(self):
        return "%s" % self.name

    def user_is_allowed(self, user):
        return (user in self.allowed_users.all()) or user.is_staff

    def user_requires_tutor(self, user):
        if user.is_staff: return False
        return self.tutor_required_count > self.count_usages(user)

    def user_requires_tutor_once(self, user):
        if user.is_staff: return False
        if self.count_usages(user) > 0:
            nr_of_latest_sessions = MachineSession.objects.filter(~Q(start=None), ~Q(end=None), machine__group_name=self.group_name, user=user, end__gt=now() - timedelta(days=31 * self.tutor_required_once_after_month)).count()
            if nr_of_latest_sessions == 0:
                return True
        return False

    def user_can_tutor(self, tutor):
        if tutor.is_staff: return True
        return self.user_requires_tutor(tutor) is False and self.user_requires_tutor_once(tutor) is False

    def count_usages(self, user):
        qs = MachineSession.objects.filter(~Q(start=None), ~Q(end=None), machine__group_name=self.group_name, user=user).values('created')
        grouped = itertools.groupby(qs, lambda d: d.get('created').strftime('%Y-%m-%d'))
        return len([ True for _, _ in grouped])

    def get_price(self, paying_user_profile):
        price_per_usage, price_per_hour = 0, 0
        if paying_user_profile.commercial_account:
            if self.price_per_hour  is not None : price_per_hour = self.price_per_hour.commercial
            if self.price_per_usage is not None : price_per_usage = self.price_per_usage.commercial
        elif paying_user_profile.commercial_account:  # discount account
            if self.price_per_hour  is not None: price_per_hour = self.price_per_hour.discount
            if self.price_per_usage is not None: price_per_usage = self.price_per_usage.discount
        else:
            if self.price_per_hour  is not None: price_per_hour = self.price_per_hour.default
            if self.price_per_usage is not None: price_per_usage = self.price_per_usage.default
        return price_per_usage, price_per_hour

    def requires_payment(self, paying_user_profile):
        price_per_usage, price_per_hour = self.get_price(paying_user_profile)
        return price_per_usage > 0 or price_per_hour > 0

class MachineSession(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="MachineSessionsUser")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="MachineSessionsTutor", blank=True, null=True)
    autologout_at = models.DateTimeField(default=None, blank=True, null=True)
    start = models.DateTimeField(default=None, blank=True, null=True)
    end = models.DateTimeField(default=None, blank=True, null=True)
    comment = models.CharField(max_length=10000, blank=True)
    rating_clean = models.IntegerField(default=-1)

    @property
    def autologout_timediff(self):
        if self.autologout_at is not None:
            timediff_total_minutes = int(math.ceil((self.autologout_at - now()).total_seconds() / 60))
            timediff_minutes = timediff_total_minutes % 60
            timediff_hours = int((timediff_total_minutes - timediff_minutes) / 60)
            return timediff_total_minutes, timediff_hours, timediff_minutes

    def __str__(self):
        return "%s;%s" % (self.machine.name, self.start)


#
# PAYED ACTIONS
#
class MachineSessionPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    machinesession = models.OneToOneField(MachineSession, on_delete=models.CASCADE, related_name="machineSessionPayment", blank=True, null=True)
    price_per_hour = models.FloatField(default=0)  # in euro
    price_per_usage = models.FloatField(default=0)  # in euro
    start = models.DateTimeField(blank=True, null=True, default=None)
    end = models.DateTimeField(blank=True, null=True, default=None)
    price = models.FloatField(default=0)
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, blank=True, null=True, related_name="machineSessionPayments")
    invoice = models.ForeignKey("Invoice", on_delete=models.SET_NULL, blank=True, null=True, related_name="machineSessionPayments")

class MaterialPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="materialPaymentsUser", verbose_name='Benutzer')  ## the user that actually pays
    machinesession = models.ForeignKey(MachineSession, on_delete=models.CASCADE, related_name="materialpayments", blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="materialPaymentsCreator", verbose_name='Erstellt durch')  # the user that created this payment
    price = models.FloatField(default=0)
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, blank=True, null=True, related_name="materialPayments")
    invoice = models.ForeignKey("Invoice", on_delete=models.SET_NULL, blank=True, null=True, related_name="materialPayments")

class PrepaidDepositPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prepaidDepositPayments", verbose_name='Benutzer')
    for_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prepaidDepositPaymentsForOther", verbose_name='Für Benutzer', default=None, blank=True, null=True)  # the user that created this payment
    price = models.FloatField(default=0)
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, blank=True, null=True, related_name="prepaidDepositPayments")
    invoice = models.ForeignKey("Invoice", on_delete=models.SET_NULL, blank=True, null=True, related_name="prepaidDepositPayments")
    def __str__(self):
        return "Deposit %s for %s" % (self.price, self.for_user)

class SpaceRentPayment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spaceRentPayments", verbose_name='Benutzer')
    for_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spaceRentPaymentsForOther", verbose_name='Für Benutzer', default=None, blank=True, null=True)  # the user that created this payment
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    price = models.FloatField(default=0)
    type = models.CharField(max_length=100, default=SpaceRentPaymentType.monthly, blank=True, null=True)
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, blank=True, null=True, related_name="spaceRentPayments")
    invoice = models.ForeignKey("Invoice", on_delete=models.SET_NULL, blank=True, null=True, related_name="spaceRentPayments")

    def __str__(self):
        if self.type == SpaceRentPaymentType.monthly:
            s = "Monatsmiete"
        else:
            s = "Tagesmiete"
        return "%s für %s" % (s, self.for_user)



#
# PAYMENTS
#
class Invoice(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    due = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    taxes = models.FloatField(default=0)
    total = models.FloatField(default=0) # with taxes if needed
    transaction = models.OneToOneField("Transaction", on_delete=models.SET_NULL, blank=True, null=True, related_name="invoice")
    include_tax = models.BooleanField(default=False)  # == mit mwst, rechnung oder spendenquittung
    type = models.CharField(max_length=100, default=InvoiceType.receipt, blank=True,null=True)


class Transaction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    comment = models.CharField(max_length=10000, default="", blank=True,null=True)
    type = models.CharField(max_length=100, default="", blank=True,null=True)
    authorized_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="authorized_transactions")

    def __str__(self):
        return self.type + ", " + self.user.username + ", " + "%s" % self.value + "Euro"

#
# FUNCTIONS
#
@receiver(pre_save, sender=Token)
def Token__update_identifier(sender, instance, *args, **kwargs):
    if instance.identifier == "":
        uid = "%s" % uuid.uuid4()
        uid = "".join(uid.split("-")[-3:])  # 20 zeichen, 48 max
        if instance.profile is not None:
            instance.identifier = "U:%s" % instance.profile.user.username
        if instance.machine is not None:
            instance.identifier = "M:%s" % instance.machine.name
        instance.identifier = instance.identifier[:28]
        instance.identifier = "%s;%s" % (instance.identifier, uid)


@receiver(post_save, sender=User)
def User__add_profile(sender, instance, *args, **kwargs):
    if not hasattr(instance, "profile"):
        instance.profile = Profile()
        instance.profile.save()
        instance.save()
        token = Token()
        token.enabled = True
        token.can_write = True
        token.profile = instance.profile
        token.save()


@receiver(post_save, sender=Machine)
def Machine__create_token(sender, instance, *args, **kwargs):
    if instance.tokens.all().count() == 0:
        token = Token()
        token.enabled = True
        token.can_write = False
        token.machine = instance
        token.save()

'''
@receiver(post_save, sender=Invoice)
def Invoice__collect_payments(sender, instance, *args, **kwargs):
    return
    total_payments = instance.materialPayments.all().count() + instance.machineSessionPayments.all().count()
    total_to_pay = 0

    if total_payments == 0:  # check that invoice is new
        unpayed_machine_sessions = MachineSessionPayment.objects.filter(~Q(end=None), user=instance.user, invoice=None, transaction=None)
        unpayed_materials = MaterialPayment.objects.filter(user=instance.user, invoice=None, transaction=None)
        for unpayed_machine_session in unpayed_machine_sessions:
            total_to_pay += unpayed_machine_session.price
            unpayed_machine_session.invoice = instance
            unpayed_machine_session.save()
        for unpayed_material in unpayed_materials:
            total_to_pay += unpayed_material.price
            unpayed_material.invoice = instance
            unpayed_material.save()
    instance.total_payment = total_to_pay
    instance.save()
'''