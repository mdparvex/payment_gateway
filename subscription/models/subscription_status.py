from django.db import models
from rest_framework import serializers
from .subscribe_vendor import SubscribeVendor


class SubscriptionStatus(models.Model):
    status_id = models.BigAutoField(primary_key=True)
    login_access_code = models.CharField(max_length=100)
    subscription_id = models.CharField(max_length=200)
    subscription_status = models.BooleanField(default=False)
    subscribe_vendor = models.ForeignKey(SubscribeVendor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscription_id', 'login_access_code', 'subscribe_vendor')

    def __str__(self):
        return str(self.login_access_code)


class SubscriptionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionStatus
        fields = '__all__'