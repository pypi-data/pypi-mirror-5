"""Admins for the models of the ``paypal_express_checkout`` app."""
from django.contrib import admin

from . import models


class ItemAdmin(admin.ModelAdmin):
    """Custom admin for the ``Item`` model."""
    list_display = ['name', 'description_short', 'value']
    search_fields = ['name', 'description']

    def description_short(self, obj):
        return '{0}...'.format(obj.description[:50])


class PaymentTransactionAdmin(admin.ModelAdmin):
    """Custom admin for the ``PaymentTransaction`` model."""
    list_display = [
        'date', 'user', 'user_email', 'transaction_id', 'value', 'status']
    search_fields = [
        'transaction_id', 'status', 'user__email', 'user__username']
    list_filter = ['status']
    raw_id_fields = ['user', ]

    def user_email(self, obj):
        return obj.user.email


class PaymentTransactionErrorAdmin(admin.ModelAdmin):
    """Custom admin for the ``PaymentTransactionError`` model."""
    list_display = [
        # FIXME 'transaction_id'
        'date', 'user', 'user_email', 'response_short',
    ]

    def user_email(self, obj):
        return obj.user.email

    def response_short(self, obj):
        return '{0}...'.format(obj.response[:50])

    def transaction_id(self, obj):
        return obj.transaction_id


class PurchasedItemAdmin(admin.ModelAdmin):
    """Custom admin for the ``PurchasedItem`` model."""
    list_display = [
        'date', 'user', 'user_email', 'transaction', 'item', 'price',
        'quantity', 'subtotal', 'total', 'status', ]
    list_filter = [
        'transaction__status', 'item', ]
    search_fields = [
        'transaction__transaction_id', 'user__email', ]
    raw_id_fields = ['user', 'transaction', ]

    def date(self, obj):
        return obj.transaction.date

    def status(self, obj):
        return obj.transaction.status

    def subtotal(self, obj):
        price = 0
        if obj.item is not None:
            price = obj.item.value
        if obj.price:
            price = obj.price
        return price * obj.quantity

    def total(self, obj):
        return obj.transaction.value

    def user_email(self, obj):
        return obj.user.email


admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.PaymentTransaction, PaymentTransactionAdmin)
admin.site.register(
    models.PaymentTransactionError, PaymentTransactionErrorAdmin)
admin.site.register(models.PurchasedItem, PurchasedItemAdmin)
