from django.db import models
import uuid
from .customer import Customer
from .price import Price
from datetime import timedelta, datetime

def get_unique_order_id():
    return 'order_' + str(uuid.uuid4())


class Order(models.Model):
    PLAN_CHOICES = (
        ('day', 'Daily'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('year', 'Yearly')
    )
    oid = models.BigAutoField(primary_key=True)
    order_id = models.CharField(default=get_unique_order_id, max_length=250, unique=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    order_data = models.JSONField(null=True,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    cancel_date = models.DateTimeField(blank=True,null=True)
    order_price = models.ForeignKey(Price,null=True,blank=True, on_delete=models.DO_NOTHING)
    #primary_price_coupon = models.ManyToManyField(Coupons, blank=True, related_name='primary_price_coupon')
    #upsell_price = models.ManyToManyField(UpsellCouponOrder, blank=True, related_name='upsell_coupon_combo')
    total_amount_charged = models.FloatField(default=0.0)
    plan_type = models.CharField(max_length=10, default='month', choices=PLAN_CHOICES)
    cancel_requested = models.BooleanField(default=False)

    customer_order_id = models.CharField(max_length=240, null=True, blank=True)

    def __str__(self):
        return self.order_id
    
    def get_future_cancel_date(self):
        if self.plan_type == 'month':
            new_date = datetime.now() + timedelta(days=30)
        elif self.plan_type == 'day':
            new_date = datetime.now() + timedelta(days=1)
        elif self.plan_type == 'week':
            new_date = datetime.now() + timedelta(days=7)
        else:
            #@TODO need to verify if it is past 1 year
            twelve_month = 30*12
            new_date = datetime.now() + timedelta(days=twelve_month)
        return new_date