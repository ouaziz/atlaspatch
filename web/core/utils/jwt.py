# utils/jwt.py
import jwt, time
from django.conf import settings

def make_access_token(agent_id: str) -> str:
    now = int(time.time())
    payload = {
        "sub": agent_id,        # identifiant de l’agent
        "iat": now,             # issued-at
        "exp": now + settings.JWT_LIFETIME
    }
    return jwt.encode(payload,
                      settings.JWT_PRIVATE_KEY,
                      algorithm=settings.JWT_ALGORITHM)


def validate_access_token(token: str) -> str:
    try:
        return jwt.decode(token,
                          settings.JWT_PUBLIC_KEY,
                          algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Expired token")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")