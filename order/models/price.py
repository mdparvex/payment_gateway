from django.db import models
import uuid

def get_unique_price_id():
    return 'price_' + str(uuid.uuid4())

class Price(models.Model):
    PLAN_CHOICES = (
        ('day', 'Daily'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('year', 'Yearly')
    )
    pid = models.BigAutoField(primary_key=True)
    price_id = models.CharField(default=get_unique_price_id, max_length=250, unique=True)
    #campaign = models.ForeignKey(Campaign, on_delete=models.DO_NOTHING)
    price_point = models.FloatField(default=0.0)
    free_days = models.IntegerField(default=0)
    free_value = models.FloatField(default=0.0)
    plan_duration_days = models.CharField(max_length=10,default='month', choices=PLAN_CHOICES)
    is_primary = models.BooleanField(default=True)
    #coupons = models.ManyToManyField(Coupons, related_name='coupon_prices', blank=True)

    title = models.CharField(max_length=140, default="Price Title")
    description= models.TextField(default="Description")
    pricing_description = models.TextField(blank=True)
    discount_description = models.TextField(blank=True)
    ordering = models.IntegerField(default=0)

    #upsell_allowed = models.ManyToManyField(UpsellPrice, related_name='upsell_prices', blank=True)
    custom_price_id = models.JSONField(default=None, blank=True, null=True)

    custom_banner_image = models.CharField(null=True, max_length=100, blank=True)

    def __str__(self):
        return self.price_id