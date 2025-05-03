from django.urls import path
from .views.subscription_view import *

urlpatterns = [
    path('initiat/payment/', subscription_initiation),
    path('webhook/', webhook_vendor),
    path('get/internal-key/<str:vendor_name>/', get_internal_api_key),
    path('get/subscription/status/', check_vendor_subscription_status),
]
