from django.conf import settings
from django.shortcuts import HttpResponse, redirect,render
import re


class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class RbacMiddleware(MiddlewareMixin):
    """
    检查用户的url请求是否是其权限范围内
    """
    def process_request(self, request):
        # print ('test')
        response = self.get_response(request)
        request_url = request.path_info
        permission_url = request.session.get(settings.SESSION_PERMISSION_URL_KEY)
        # print('访问url',request_url)
        # print('权限--',permission_url)
        # 如果请求url在白名单，放行
        # print (settings.SAFE_URL)
        for url in settings.SAFE_URL:
            # print(url)
            # print(request_url)
            # print (re.match(url, request_url))
            if re.match(url, request_url):
                if re.match(url, request_url):
                    if '/login/' not in request_url and '/logout/' not in request_url and '/index/' not in request_url and '/admin' not in request_url and request_url in str(url):
                        # print(path, 'path')
                        response.set_cookie('current_page_DMS', value=request_url)
                        # request.session.set_expiry(
                        #     7 * 12 * 60 * 60)  # None：会使用全局的session配置。在settings.py中可以设置SESSION_COOKIE_AGE来配置全局的过期时间。默认是1209600秒，也就是2周的时间。

                    return response

        # 如果未取到permission_url, 重定向至登录；为了可移植性，将登录url写入配置
        if not permission_url:
            # print("2")
            return redirect(settings.LOGIN_URL)

        # 循环permission_url，作为正则，匹配用户request_url
        # 正则应该进行一些限定，以处理：/user/ -- /user/add/匹配成功的情况
        flag = False
        for url in permission_url:
            url_pattern = settings.REGEX_URL.format(url=url)
            # print (url_pattern)
            # print (request_url)
            # print(re.match(url, request_url))
            if re.match(url_pattern, request_url):
                flag = True
                if '/login/' not in request_url and '/logout/' not in request_url and '/index/' not in request_url and '/admin' not in request_url and request_url in str(url):
                    # print(path, 'path')
                    response.set_cookie('current_page_DMS', value=request_url)
                    # request.session.set_expiry(
                    #     7 * 12 * 60 * 60)
                break
        if flag:
            return response
        else:
            # 如果是调试模式，显示可访问url
            if settings.DEBUG:
                info ='<br/>' + ( '<br/>'.join(permission_url))
                # return HttpResponse('无权限，请尝试访问以下地址：%s' %info)
                # return HttpResponse('您的账户无权限访问')
                Skin = request.COOKIES.get('Skin_raw')
                # print(Skin)
                if not Skin:
                    Skin = "/static/src/blue.jpg"
                # weizhi = "Lesson-Learn/Reliability/Upload"
                message= '您的账户无权限访问'
                return render(request, 'NoPerm.html', locals())
            else:
                # return HttpResponse('无权限访问')
                # info = '<br/>' + ('<br/>'.join(permission_url))
                info = ""
                # for i in permission_url:
                #     info = info + "\n" + i
                # return HttpResponse('无权限，请尝试访问以下地址：%s' %info)
                # return HttpResponse('您的账户无权限访问')
                Skin = request.COOKIES.get('Skin_raw')
                # print(Skin)
                if not Skin:
                    Skin = "/static/src/blue.jpg"
                weizhi = "Warning"
                message = "您的账户无权限访问,请尝试访问以下地址(点击跳转)："
                messageurl = permission_url
                return render(request, 'NoPerm.html', locals())
                # return render(request, 'NoPerm.html', {'message': '无权限访问'})