from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile
    fk_name = 'user'


class MachineUsersInline(admin.TabularInline):
    model = models.Machine.allowed_users.through
    fk_name = 'user'

class ProfileAdmin(BaseUserAdmin):
    list_display = ("first_name", "last_name", "company_name", "deposit", "email", "is_staff", "allow_invoice", "paying_user")
    inlines = (ProfileInline, MachineUsersInline)

    def company_name(self, obj):
        return obj.profile.company_name

    def deposit(self, obj):
        return obj.profile.prepaid_deposit

    def allow_invoice(self, obj):
        return obj.profile.allow_invoice

    def paying_user(self, obj):
        return obj.profile.paying_user


@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "enabled", "can_write", "assigned_to", "identifier")
    list_filter = ( "created", "enabled", "can_write")
    list_display_links = ["id", "assigned_to"]

    def assigned_to(self, obj):
        v = obj.machine
        if v is None:
            v = obj.profile
        if v is None:
            return "Not assigned"
        return v


@admin.register(models.Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "comment", "ask_clean", "ask_pay_material", "price_per_hour", "price_per_usage","tutor_required_count", "tutor_required_once_after_month", "current_session")

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "user", "value", "type", "comment")
    list_filter = ( "type",)

    def user(self, obj):
        return obj.profile.user


@admin.register(models.MachineSessionPayment)
class MachineSessionPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "machine", "machinesession", "start", "end", "price", "transaction", "invoice")
    list_filter = ("start", "end")
    list_display_links = ["id", "machine", "machinesession"]

    def machine(self, obj):
        try:
            return obj.machinesession.machine
        except:
            return None

@admin.register(models.MachineSession)
class MachineSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "user", "tutor", "paying_user", "start", "end", "rating_clean", "machineSessionPayments")
    list_filter = ( "machine", "start", "end", "rating_clean")
    list_display_links = ["id", "machine", "user", "tutor", "paying_user", "machineSessionPayments"]

    def machine(self, obj):
        return obj.machine

    def paying_user(self, obj):
        if obj.machineSessionPayments is not None:
            return obj.machineSessionPayments.user
        return None


@admin.register(models.MaterialPayment)
class MaterialPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "user", "creator", "price", "transaction", "invoice")
    list_filter = ( "created", )

@admin.register(models.SpaceRentPayment)
class SpaceRentPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created", "start", "end", "price", "type","transaction", "invoice")
    list_filter = ( "created", )


admin.site.register(models.Invoice)
admin.site.register(models.SpaceAccessTracking)
admin.site.unregister(User)
admin.site.register(User, ProfileAdmin)
