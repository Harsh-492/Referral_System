from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import User
from .serializers import UserSerializer


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = request.POST
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            referral_code = data.get('referral_code')
            if referral_code:
                referred_by = User.objects.filter(referral_code=referral_code).first()
                if referred_by:
                    # Logic to give points to the user who referred this user
                    pass
            return JsonResponse({'user_id': user.id, 'message': 'User registered successfully'})
        else:
            return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request):
    user = request.user
    serializer = UserSerializer(user)
    return JsonResponse(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def referrals(request):
    user = request.user
    referral_code = user.referral_code
    if referral_code:
        referred_users = User.objects.filter(referral_code=referral_code)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(referred_users, request)
        serializer = UserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return JsonResponse({'message': 'No referrals found for this user'}, status=404)