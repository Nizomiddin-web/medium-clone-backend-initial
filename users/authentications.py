from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication, AuthUser
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token

from users.enums import TokenType        # keyinroq ushbu faylni yaratib olamiz
from users.services import TokenService

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        user, access_token = super().authenticate(request)

        if not self.is_valid_access_token(user, access_token):
            raise AuthenticationFailed("Access tokeni yaroqsiz")

        return user, access_token

    @classmethod
    def is_valid_access_token(cls, user: User, access_token: Token) -> bool:
        valid_access_tokens = TokenService.get_valid_tokens(user.id, TokenType.ACCESS)

        if (
                valid_access_tokens
                and str(access_token).encode() not in valid_access_tokens
        ):
            raise AuthenticationFailed("Kirish ma'lumotlari yaroqsiz")
        return True