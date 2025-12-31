from rest_framework_jwt.utils import jwt_decode_handler
import jwt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

class JwtAuthentication(BaseJSONWebTokenAuthentication):
    def authenticate(self, request):
        # 认证逻辑()
        # token信息可以放在请求头中,请求地址中
        # key值可以随意叫
        # token=request.GET.get('token')  # token放到请求地址中
        # token放到请求头中 , key 必须为: Authorization
        token = request.META.get('HTTP_Authorization'.upper())
        # 校验token是否合法
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            raise AuthenticationFailed('过期了')
        except jwt.DecodeError:
            raise AuthenticationFailed('解码错误')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('不合法的token')
        user = self.authenticate_credentials(payload)
        return (user, token)