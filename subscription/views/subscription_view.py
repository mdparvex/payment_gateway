from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import importlib
from ..models.subscribe_vendor import SubscribeVendor
from ..models.subscription_status import SubscriptionStatus


@api_view(['GET'])
def get_internal_api_key(request, vendor_id):
    content = {
        "status": 0
    }

    return JsonResponse(content, status=status.HTTP_200_OK)

@api_view(['POST'])
def subscription_initiation(request):
    content = {
        'status': 0
    }
    try:
        if 'internal_api_key' in request.data:
            internal_api_key = request.data['internal_api_key']

            query_params = request.data

            query_params.pop('internal_api_key', None)

            try:
                subscribe_vendor = SubscribeVendor.objects.get(internal_api_key=internal_api_key)
            except:
                content['message'] = 'Bad Request Invalid api key'
                return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

            
            try:
                print("subscription.classes.vendors." + subscribe_vendor.vendor_name)
                module = importlib.import_module("subscription.classes.vendors." + subscribe_vendor.vendor_name)
            except Exception as e:
                print(e)
                content['message'] = 'Bad Request'
                return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)
            print(module)
            vendor_class = getattr(module, subscribe_vendor.vendor_name)
            vendor_obj = vendor_class()
            get_response = vendor_obj.custom(data=query_params, vendor_obj=subscribe_vendor)
            content['message'] = 'Success'
            content['status'] = 1
            content['data'] = get_response
            return JsonResponse(content, status=status.HTTP_200_OK)
        else:
            content['message'] = 'Require parameter missing'
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        content['message'] = str(e)
        return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def webhook_vendor(request, vendor_id):
    content = {
        "status": 0
    }
    # print(request.data)
    try:
        subscribe_vendor = SubscribeVendor.objects.get(subscribe_vendor_id=vendor_id)
    except:
        content['message'] = 'Bad Request Invalid api key'
        return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

    try:
        module = importlib.import_module("subscription.classes.vendors." + subscribe_vendor.vendor_name)
    except:
        content['message'] = 'Bad Request'
        return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

    vendor_class = getattr(module, subscribe_vendor.vendor_name)
    vendor_obj = vendor_class()
    get_response = vendor_obj.webhook(request=request, vendor=subscribe_vendor)

    if isinstance(get_response, str):
        content['Flag'] = get_response
    else:
        content['Flag'] = ""

    content['message'] = 'Success'
    content['status'] = 1
    return JsonResponse(content, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def check_vendor_subscription_status(request):
    content = {
        'status': 0
    }
    if 'login_access_code' in request.data and 'internal_api_key' in request.data:
        internal_api_key = request.data['internal_api_key']
        login_access_code = request.data['login_access_code']
        try:
            subscription = SubscriptionStatus.objects.get(login_access_code=login_access_code,
                                                          subscribe_vendor__internal_api_key=internal_api_key)
            content['message'] = 'Success'
            content['status'] = 1
            content['subscription_status'] = subscription.subscription_status
            return JsonResponse(content, status=status.HTTP_200_OK)
        except:
            content['message'] = 'Bad Request'
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        content['message'] = 'Bad Request'
        return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)