from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
import jwt

class TrustMeAuthentication(BaseAuthentication):

    def authenticate(self, request):
        username = request.headers.get("Trust-Me")
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed(f'No user {username}')


class JWTauthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("jwt")
        if not token:
            raise AuthenticationFailed("token not found")
        decoded = jwt.decode(token, "kbh224", algorithms="HS256")
        pk = decoded.get("pk")
        if not pk:
            raise AuthenticationFailed("invalid token")
        try:
            user = User.objects.get(pk=pk)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed("user not found")