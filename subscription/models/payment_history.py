from django.db import models
from rest_framework import serializers
from .subscribe_vendor import SubscribeVendor
from order.models.order import Order

STORE_TYPES = (
    ('1', 'Stripe'),
    ('2', 'Paypal'),
    ('3', 'shopify'),
    ('4', 'Android'),
    ('5', 'iOS')
)

PAYMENT_STATUS = (
    ('1', 'Success'),
    ('2', 'Fail'),
    ('3', 'Cancelled'),
)


class PaymentHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    store_type = models.CharField(max_length=100, choices=STORE_TYPES)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField()
    status = models.CharField(max_length=100, choices=PAYMENT_STATUS)
    event_type = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.status)


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = '__all__'
