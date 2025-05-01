from rest_framework.decorators import api_view
from django.http import JsonResponse

@api_view(['POST'])
def subscription_initiation(request):
    
    return JsonResponse({'success':1})

@api_view(['POST'])
def webhook_vendor(request, vendor_id):
    
    return JsonResponse({'success':1})