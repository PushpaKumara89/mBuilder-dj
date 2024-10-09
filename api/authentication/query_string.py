from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthenticationQueryString(JWTAuthentication):
    def get_header(self, request):
        if 'jwt' in request.query_params:
            return bytes('Bearer %s' % (request.query_params['jwt']), 'utf-8')

        return super().get_header(request)
