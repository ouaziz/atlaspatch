# auth.py
from rest_framework import authentication, exceptions
from .utils.jwt import settings, jwt

class JWTAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth.split()[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,     # clé publique
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("token expired")
        return (payload["sub"], None)          # user = agent_id
