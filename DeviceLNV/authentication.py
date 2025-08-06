from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import exceptions

from django.utils.translation import gettext_lazy as _

from app01.models import UserInfo,Role


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义登录认证，使用自有用户表
    """
    username_field = 'username'

    def validate(self, attrs):
        # authenticate_kwargs = {self.username_field: attrs[self.username_field], 'password': attrs['password']}
        authenticate_kwargs = {'account': attrs[self.username_field], 'password': attrs['password']}
        # print(authenticate_kwargs,"authenticate_kwargs")
        try:
            user = UserInfo.objects.get(**authenticate_kwargs)
            # print(attrs, self, self.context['request'], "attrs")
            request = self.context['request']#没有经过login的view登录是没有写入登录用户信息的，需要增加api登录的用户信息到session中去，log里面才有用户信息输出，
            request.session['user_id_DSM'] = user.id
            request.session['user_name_DMS'] = user.username
            request.session['account_DMS'] = authenticate_kwargs['account']
            # print(request.session.get('user_id'),request.session.get('account'))
            # print(user, user.role.all(), 'user')
        except Exception as e:
            raise exceptions.NotFound(e.args[0])

        refresh = self.get_token(user)
        #edwin:只有指定role的用户才能获取Token
        if Role.objects.filter(name="API_DMS").first() not in user.role.all() and Role.objects.filter(name="admin").first() not in user.role.all():
            print(1)
            raise AuthenticationFailed("没有权限")
            return False
        else:
            data = {"userId": user.id, "token": str(refresh.access_token), "refresh": str(refresh)}
            # print(data)
        # data = {"userId": user.id, "token": str(refresh.access_token), "refresh": str(refresh)}
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyJWTAuthentication(JWTAuthentication):
    '''
    修改JWT认证类，返回自定义User表对象
    '''
    def get_user(self, validated_token):
        # print('tt')
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user = UserInfo.objects.get(**{'id': user_id})
        except UserInfo.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')
        # print(user,validated_token,"MyJWTAuthentication")

        return user
