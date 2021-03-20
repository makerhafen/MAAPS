from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
from django.contrib.auth.models import User
from django.db.models import Q
import os, uuid
from datetime import datetime, timedelta


class Token(models.Model):
    created    = models.DateTimeField(auto_now_add=True)
    updated    = models.DateTimeField(auto_now=True)
    identifier = models.CharField(max_length=48, blank=True)
    enabled    = models.BooleanField(default=False)
    can_write    = models.BooleanField(default=False) # true if terminal should show token to be written to rfid card
    profile    = models.ForeignKey("Profile", related_name="tokens", on_delete=models.CASCADE, blank=True, null=True)
    machine    = models.ForeignKey("Machine", related_name="tokens", on_delete=models.CASCADE, blank=True, null=True)

def rename_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}_{}_{}.{}'.format(instance.user.username, datetime.today().strftime('%Y-%m-%d'),("%s" % uuid.uuid4()).split("-")[0], ext)
    return os.path.join('photos/', filename)

class Profile(models.Model):
    created     = models.DateTimeField(auto_now_add=True)
    updated     =  models.DateTimeField(auto_now=True)
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    paying_user = models.OneToOneField("Profile", on_delete=models.CASCADE, blank=True, null=True)
    prepaid_deposit = models.FloatField(default=0)
    allow_invoice   = models.BooleanField(default=False)
    profile_picture = models.ImageField(blank=True, null=True, upload_to=rename_file)
    company_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        if self.company_name != "":
            return "%s, %s. %s" % (self.company_name, self.user.first_name[0].upper(), self.user.last_name)
        return "%s %s" % ( self.user.first_name, self.user.last_name )

class Machine(models.Model):
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    name            = models.CharField(max_length=200)
    comment         = models.CharField(max_length=10000, blank=True)
    ask_clean       = models.BooleanField(default=False)
    ask_pay_material= models.BooleanField(default=False)
    price_per_hour  =  models.FloatField(default=0) # in Euro
    price_per_usage =  models.FloatField(default=0) # in Euro
    tutor_required_count            = models.IntegerField(default=0) # wir oft
    tutor_required_once_after_month = models.IntegerField(default=24) # all
    currentSession    = models.ForeignKey("MachineSession", on_delete=models.SET_NULL, related_name="_current_session",blank=True, null=True)
    allowed_users     = models.ManyToManyField(User, related_name="allowed_machines")

    def __str__(self):
        return "Machine: %s" % self.name

    def user_is_allowed(self, user):
        return (user in self.allowed_users.all()) or user.is_staff

    def user_requires_tutor(self, user):
        if  user.is_staff: return False
        return self.tutor_required_count > self.count_usages(user)

    def user_requires_tutor_once(self, user):
        if user.is_staff: return False
        if self.count_usages(user) > 0:
            nr_of_latest_sessions = MachineSession.objects.filter(~Q(start=None), ~Q(end=None), machine = self, user = user, end__gt=datetime.now() - timedelta(days=self.tutor_required_once_after_month*31)).count()
            if nr_of_latest_sessions == 0 :
                return True
        return False

    def user_can_tutor(self, tutor):
        if tutor.is_staff: return True
        return self.user_requires_tutor(tutor) is False and self.user_requires_tutor_once(tutor) is False

    def count_usages(self, user):
        return MachineSession.objects.filter(~Q(start=None), ~Q(end=None), machine=self, user=user).count()

class MachineSession(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="machine_user_sessions")
    tutor   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="machine_tutor_sessions",blank=True, null=True)
    start   = models.DateTimeField(default=None, blank=True, null=True)
    end     = models.DateTimeField(default=None, blank=True, null=True)
    comment = models.CharField(max_length=10000, blank=True)
    rating_clean = models.IntegerField(default=-1)

class MachineSessionPayment(models.Model):
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    machinesession    = models.OneToOneField(MachineSession, on_delete=models.CASCADE, related_name="paymentsession",blank=True, null=True)
    transaction  = models.ForeignKey("Transaction", on_delete=models.CASCADE, blank=True, null=True,related_name="machineSessionPayments")
    invoice  = models.ForeignKey("Invoice", on_delete=models.SET_NULL, blank=True, null=True,related_name="machineSessionPayments")
    price_per_hour  =  models.FloatField(default=0) # in euro
    price_per_usage =  models.FloatField(default=0) # in euro
    totalpayment    = models.FloatField(default=0)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)

class MaterialPayment(models.Model):
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name="materialPaymentsUser",  verbose_name='Benutzer') ## the user that actually pays
    creator         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="materialPaymentsCreator",  verbose_name='Erstellt durch') # the user that created this payment
    value    = models.FloatField(default=0)
    transaction  = models.ForeignKey("Transaction", on_delete=models.CASCADE, blank=True, null=True,related_name="materialPayments")
    invoice      = models.ForeignKey("Invoice", on_delete=models.SET_NULL, blank=True, null=True,related_name="materialPayments")

class Invoice(models.Model):
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_payment = models.FloatField(default=0)
    transaction   = models.OneToOneField("Transaction", on_delete=models.SET_NULL, blank=True, null=True,related_name="invoice")

class TransactionType():
    from_cash_for_deposit     = "from_cash_for_deposit"
    from_cash_for_invoice     = "from_cash_for_invoice"
    from_bank_for_deposit     = "from_bank_for_deposit"
    from_bank_for_invoice     = "from_bank_for_invoice"
    from_deposit_for_machine  = "from_deposit_for_machine"
    from_deposit_for_material = "from_deposit_for_material"

class Transaction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    value   =  models.FloatField(default=0)
    comment = models.CharField(max_length=10000)
    type = models.CharField(max_length=10000)
    authorized_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="authorized_transactions")

    def __str__(self):
        return "Transaction for: " + self.user.username + " , " + "%s"%self.value + "Euro"


@receiver(pre_save, sender=Token)
def Token__update_identifier(sender, instance, *args, **kwargs):
    if instance.identifier == "":
        uid = "%s" % uuid.uuid4()
        uid = "".join(uid.split("-")[-3:]) # 20 zeichen, 48 max
        if instance.profile != None:
            instance.identifier = "U:%s" % (instance.profile.user.username)
        if instance.machine != None:
            instance.identifier = "M:%s" % (instance.machine.name)
        instance.identifier = instance.identifier[:28]
        instance.identifier = "%s;%s" % (instance.identifier , uid)

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
        token.can_write = True
        token.machine = instance
        token.save()

@receiver(post_save, sender=Invoice)
def Invoice__collect_payments(sender, instance, *args, **kwargs):
    total_payments = instance.materialPayments.all().count() + instance.machineSessionPayments.all().count()
    total_to_pay = 0

    if total_payments == 0:
        unpayed_machine_sessions = MachineSessionPayment.objects.filter(~Q(end=None),user=instance.user, invoice=None, transaction=None)
        unpayed_materials = MaterialPayment.objects.filter(user=instance.user, invoice=None, transaction=None)
        for unpayed_machine_session in unpayed_machine_sessions:
            total_to_pay += unpayed_machine_session.totalpayment
            unpayed_machine_session.invoice = instance
            unpayed_machine_session.save()
        for unpayed_material in unpayed_materials:
            total_to_pay += unpayed_material.value
            unpayed_material.invoice = instance
            unpayed_material.save()
    instance.total_payment = total_to_pay
