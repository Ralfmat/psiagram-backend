from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework.decorators import api_view, permission_classes
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from django.http import JsonResponse

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'postmessage'  
    client_class = OAuth2Client

def ping(request):
    return JsonResponse({"status": "ok", "app": "users"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })