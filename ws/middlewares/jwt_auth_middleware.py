from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.http.request import QueryDict
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken


@database_sync_to_async
def get_user(validated_token):
    return get_user_model().objects.filter(id=validated_token.get('user_id')).first()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()

        authorization_token = self.get_authorization_token(scope)
        authorization = JWTAuthentication()
        token = authorization.get_raw_token(authorization_token)
        try:
            token = UntypedToken(token)
            user = await get_user(validated_token=token.payload)
        except (InvalidToken, TokenError) as e:
            user = None

        scope['user'] = user

        return await super().__call__(scope, receive, send)

    def get_authorization_token(self, scope) -> str:
        return QueryDict(scope.get('query_string')).get('token', '').encode('utf8')
