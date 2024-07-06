import time
import json
from django.utils.deprecation import MiddlewareMixin
import urllib.parse
# 获取日志logger
import logging
import datetime

# logger = logging.getLogger(__name__)
logger = logging.getLogger('log')# 与loggers里自己定义的名称对应


class LogMiddle(MiddlewareMixin):
    # 日志处理中间件
    def process_request(self, request):
        # 存放请求过来时的时间
        request.init_time = time.time()
        return None

    def process_response(self, request, response):
        try:
            # # 耗时
            # localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # # 请求路径
            path = request.path
            # 请求方式
            method = request.method
            # 响应状态码
            status_code = response.status_code
            # 响应内容
            content = {}
            if method == "POST":#get返回的html，json.loads时会报错
                content = response.content
                # 记录信息
                # print('a')
                content = str(content.decode('utf-8'))
                # print('b')
                content = urllib.parse.unquote(content)
                # print('c')
                # print(content)
                content = (json.loads(content))
                # print('d')
                # message = '%s %s %s %s %s' % (localtime, path, method, status_code, content)
                # logger.info(message)
                # print('2----请求视图前被调用')
                ip = None
                proxy_ip = None
                # useraccount = request.user
                # print(useraccount.id)
                username = request.session.get('user_name_DMS')
                Account = request.session.get('account_DMS')
                # print(username,Account)
                server_name = request.META.get('SERVER_NAME')
                COMPUTERNAME = None
                USERNAME = None
                CLIENTNAME = None
                if 'COMPUTERNAME' in request.META.keys():
                    COMPUTERNAME = request.META.get("COMPUTERNAME")
                if 'USERNAME' in request.META.keys():
                    USERNAME = request.META.get("USERNAME")
                if 'CLIENTNAME' in request.META.keys():
                    CLIENTNAME = request.META.get("CLIENTNAME")
                if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
                    ip = request.META['HTTP_X_FORWARDED_FOR']
                    proxy_ip = request.META.get("REMOTE_ADDR")
                    # print(request.META)
                else:
                    ip = request.META['REMOTE_ADDR']
                    proxy_ip = request.META.get("REMOTE_ADDR")
                    # print(request.META)
                request_url = request.path_info
                dateime =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # print('时间', dateime)
                # print('用户的主机名是', server_name)
                # print('用户的ip是', ip)
                # print('用户的proxy_ip是', proxy_ip)
                # print('用户的请求路径是', request_url)
                # # content = response.content
                # print(content)
                # response = get_response(request)

                # 此处编写的代码会在每个请求处理视图之后被调用。
                # print('3----请求视图后被调用')
                # log_init().info(f'{server_name} {ip} {proxy_ip} {request_url} {}')
                # message = '%s %s %s>%s %s>%s %s %s %s %s %s' % (dateime, server_name, Account, username, CLIENTNAME, COMPUTERNAME, USERNAME, ip, proxy_ip, request_url, method, content)
                message = '%s %s>%s %s>%s>%s %s %s %s %s' % (dateime, Account, username, CLIENTNAME, COMPUTERNAME, USERNAME, ip, proxy_ip, request_url, method)
                logger.info(message)
        except Exception as e:
            logger.critical('系统错误%s' % str(e))
        return response

# def simple_middleware(get_response):  # 自定义类中间件
#     # 此处编写的代码仅在Django第一次配置和初始化的时候执行一次。
#     print('1----django启动了')
#
#     def middleware(request):  # 自定义中间键函数
#         # 此处编写的代码会在每个请求处理视图前被调用。
#         print('2----请求视图前被调用')
#         ip = None
#         proxy_ip = None
#         server_name = request.META.get('SERVER_NAME')
#         if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
#             ip = request.META['HTTP_X_FORWARDED_FOR']
#             proxy_ip = request.META.get("REMOTE_ADDR")
#         else:
#             ip = request.META['REMOTE_ADDR']
#         request_url = request.path_info
#         dateime = datetime.datetime.now()
#         print('时间', dateime)
#         print('用户的主机名是', server_name)
#         print('用户的ip是', ip)
#         print('用户的proxy_ip是', proxy_ip)
#         print('用户的请求路径是', request_url)
#         response = get_response(request)
#
#         # 此处编写的代码会在每个请求处理视图之后被调用。
#         print('3----请求视图后被调用')
#         # log_init().info(f'{server_name} {ip} {proxy_ip} {request_url} {}')
#         logger.info(f'{dateime} {server_name} {ip} {proxy_ip} {request_url}')
#         return response
#
#     return middleware
