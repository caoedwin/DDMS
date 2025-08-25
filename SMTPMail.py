import requests
import io
import asyncio
import traceback
from aiosmtplib import SMTP, SMTPException, SMTPServerDisconnected
from datetime import date
import datetime, os, json
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import socket


def ImportPersonalInfo(Customer='', SAPNum='', GroupNum='', Status='', DepartmentCode=''):
    # url = r'http://127.0.0.1:8002/PersonalInfo/api_Per/login/'
    # url2 = r'http://127.0.0.1:8002/PersonalInfo/Perapi/?'
    url = r'http://192.168.1.9:8002/PersonalInfo/api_Per/login/'
    url2 = r'http://192.168.1.9:8002/PersonalInfo/Perapi/?'
    requests.adapters.DEFAULT_RETRIES = 1
    # s = requests.session()
    # s.keep_alive = False  # 关闭多余连接
    # getTestSpec=requests.get(url)
    # headers = {'Connection': 'close'}
    try:
        headers = \
            {
                "Content-Type": "application/json;charset=UTF-8"
            }
        body = \
            {
                "username": "API_CQM", "password": "Qs!3m6Tc7"
            }
        r = requests.post(url, headers=headers, data=json.dumps(body))
    except:
        # time.sleep(0.1)
        print("Can't connect to DDIS Sercer or get token failed")
        return 0
    # print(json.loads(r.text)["token"])
    if json.loads(r.text)["token"]:
        Auth_token = "Bearer " + json.loads(r.text)["token"]
        try:
            # GroupNum = "C1010S3"
            headers = \
                {
                    "Authorization": Auth_token
                }
            content = \
                {
                    "Customer": Customer,
                    "SAPNum": SAPNum,
                    "GroupNum": GroupNum,
                    "Status": Status,
                    "DepartmentCode": DepartmentCode,
                }
            getTestSpec = requests.get(url2, headers=headers, params=content)
        except:
            # time.sleep(0.1)
            print("Got nothing, try request agian")
            return 0
        return getTestSpec.json()


def ImportDeviceInfo(Customer='', NID='', BR_per_code='', BrwStatus='', DevStatus=''):
    url = r'http://192.168.1.9:8004/DeviceLNV/api/login/'
    url2 = r'http://192.168.1.9:8004/DeviceLNV/DeviceLNV_api/?'
    # url = r'http://127.0.0.1:8003/DeviceLNV/api/login/'
    # url2 = r'http://127.0.0.1:8003/DeviceLNV/DeviceLNV_api/?'
    requests.adapters.DEFAULT_RETRIES = 1
    try:
        headers = \
            {
                "Content-Type": "application/json;charset=UTF-8"
            }
        body = \
            {
                "username": "API_DMS", "password": "dX6c9T0i"
            }
        r = requests.post(url, headers=headers, data=json.dumps(body))
    except Exception as e:
        # time.sleep(0.1)
        print(str(e))
        return 0
    # print(json.loads(r.text)["token"])
    if json.loads(r.text)["token"]:
        Auth_token = "Bearer " + json.loads(r.text)["token"]
        try:
            # GroupNum = "C1010S3"
            headers = \
                {
                    "Authorization": Auth_token
                }
            content = \
                {
                    "Customer": Customer,
                    "NID": NID,
                    "BR_per_code": BR_per_code,
                    "BrwStatus": BrwStatus,
                    "DevStatus": DevStatus,
                }
            getTestSpec = requests.get(url2, headers=headers, params=content)
        except:
            print("Got nothing, try request agian")
            return 0
        return getTestSpec.json()


def create_excel_in_memory(data_list):
    # 创建DataFrame
    df = pd.DataFrame(data_list)

    # 将Excel文件保存到BytesIO对象（内存中）
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='设备报告')

    excel_buffer.seek(0)  # 移动到文件开头
    return excel_buffer.read()


def test_smtp_connection():
    """测试SMTP服务器连接"""
    try:
        # 测试网络连通性
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('10.128.2.181', 25))
        if result == 0:
            print("✓ 可以连接到 SMTP 服务器")
            return True
        else:
            print("✗ 无法连接到 SMTP 服务器")
            return False
        sock.close()
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False


def sync_send_email(devicelist, email_list):
    """同步方式发送邮件"""
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = 'DDMS@Compal.com'

        # 过滤和验证收件人地址
        valid_recipients = []
        for email in email_list:
            if email and isinstance(email, str) and '@' in email and '.' in email.split('@')[-1]:
                valid_recipients.append(email.strip())

        # 确保至少有一个有效收件人
        if not valid_recipients:
            valid_recipients = ['Edwin_Cao@compal.com']
            print("警告：没有有效的收件人，使用默认地址")

        msg['To'] = ", ".join(valid_recipients)
        msg['Cc'] = 'DQA_LNV_Managers@compal.com'
        # msg['Cc'] = 'Edwin_Cao@compal.com'
        msg['Subject'] = '【APDQA設備超期提醒】'

        # 添加邮件正文
        if len(devicelist) == 0:
            body_html = """
            <html>
                <body>
                    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <p>Dear all,</p>
                        <p style="color: #009900; font-weight: bold;">
                            本期沒有設備超期，謝謝。
                        </p>
                        <div style="margin-top: 40px; font-size: 0.9em; color: #d9534f;">
                            <p>此邮件由系统自动发送，请勿回复</p>
                            <p>APDQA 设备管理系统</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            body = MIMEText(body_html, "html", "utf-8")
        else:
            body_html = f"""
            <html>
                <body>
                    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <p>Dear all,</p>
                        <p style="color: #d9534f; font-weight: bold;">
                            你有設備超期！！！請立即預約歸還！！！
                        </p>
                        <h2>设备报告数据</h2>
                        <p>附件是完整的设备报告数据，请查收。</p>
                        <p>此邮件包含 {len(devicelist)} 条设备记录。</p>
                        <p style="margin-top: 30px;">
                            <a href="http://10.129.83.21:8004/DeviceLNV/R_Borrowed/" 
                            style="background-color: #337ab7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                            立即预约归还
                            </a>
                        </p>
                        <div style="margin-top: 40px; font-size: 0.9em; color: #d9534f;">
                            <p>此邮件由系统自动发送，请勿回复</p>
                            <p>APDQA 设备管理系统</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            body = MIMEText(body_html, "html", "utf-8")

        msg.attach(body)

        # 添加附件（只在有数据时）
        if devicelist:
            excel_data = create_excel_in_memory(devicelist)
            attachment = MIMEApplication(excel_data, Name="设备报告.xlsx")
            attachment['Content-Disposition'] = 'attachment; filename="设备报告.xlsx"'
            msg.attach(attachment)

        # 发送邮件
        with smtplib.SMTP('10.128.2.181', 25, timeout=30) as server:
            # 构建收件人列表（To + Cc）
            all_recipients = []

            # 处理To收件人
            if 'To' in msg:
                to_addresses = [addr.strip() for addr in msg['To'].split(',')
                                if addr.strip() and '@' in addr.strip()]
                all_recipients.extend(to_addresses)

            # 处理Cc收件人
            if 'Cc' in msg:
                cc_addresses = [addr.strip() for addr in msg['Cc'].split(',')
                                if addr.strip() and '@' in addr.strip()]
                all_recipients.extend(cc_addresses)

            # 确保至少有一个收件人
            if not all_recipients:
                all_recipients = ['Edwin_Cao@compal.com']

            print(f"最终收件人列表: {all_recipients}")

            # 使用sendmail方法发送，避免空地址问题
            from_email = 'DDMS@Compal.com'
            server.sendmail(from_email, all_recipients, msg.as_string())

            print('✓ 同步邮件发送成功')
            return True

    except Exception as e:
        print(f"同步邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def simple_test_email():
    """发送简单的测试邮件"""
    try:
        msg = MIMEMultipart()
        msg['From'] = 'DDMS@Compal.com'
        msg['To'] = 'Edwin_Cao@compal.com'
        msg['Subject'] = 'SMTP连接测试'

        body = MIMEText('这是一封测试邮件，用于验证SMTP连接是否正常。', 'plain', 'utf-8')
        msg.attach(body)

        with smtplib.SMTP('10.128.2.181', 25, timeout=30) as server:
            server.sendmail('DDMS@Compal.com', ['Edwin_Cao@compal.com'], msg.as_string())
            print('✓ 测试邮件发送成功')
            return True

    except Exception as e:
        print(f"测试邮件发送失败: {e}")
        return False


if __name__ == "__main__":
    try:
        print("开始执行设备超期检查...")

        # 测试网络连接
        print("测试SMTP服务器连接...")
        if not test_smtp_connection():
            print("SMTP服务器连接失败，程序退出")
            exit(1)

        # 发送测试邮件
        # print("发送测试邮件...")
        # if not simple_test_email():
        #     print("测试邮件发送失败，程序退出")
        #     exit(1)

        # 获取设备数据
        print("获取设备数据...")
        Devicelist0 = ImportDeviceInfo(BrwStatus='已借出') or []
        Devicelist1 = ImportDeviceInfo(BrwStatus='驗收中') or []
        Devicelist2 = ImportDeviceInfo(BrwStatus='固定設備') or []
        Devicelist3 = ImportDeviceInfo(BrwStatus='預定確認中') or []
        Devicelist4 = ImportDeviceInfo(BrwStatus='續借確認中') or []

        # 合并设备列表
        all_devices0 = Devicelist0 + Devicelist1 + Devicelist2 + Devicelist3 + Devicelist4
        all_devices = [item for item in all_devices0 if item['DevStatus'] != 'Damaged' and item['DevStatus'] != 'Lost']
        print(f"总共获取到 {len(all_devices)} 台设备")

        # 检查超期设备
        Num = 0  # 超过多少天提醒
        today = date.today()
        devicelist = []

        for item in all_devices:
            if item.get("Plandate"):
                try:
                    plan_date = date.fromisoformat(item["Plandate"])
                    over_days = (today - plan_date).days
                    if over_days > Num:
                        item_copy = item.copy()
                        item_copy["OverDay"] = over_days
                        devicelist.append(item_copy)
                except ValueError:
                    continue

        print(f"发现 {len(devicelist)} 台超期设备")

        # 获取人员信息
        Pers_list = ImportPersonalInfo(Customer='') or []
        group_info_map = {
            p['GroupNum']: (p['DepartmentCode'], p['EngName'])
            for p in Pers_list if p.get('GroupNum')
        }

        # 添加部门和邮箱信息
        for device in devicelist:
            group_key = device.get('BR_per_code', '')
            dept_code, eng_name = group_info_map.get(group_key, ('', ''))

            device['Department'] = dept_code if dept_code else ''

            if eng_name:
                # 清理英文名中的特殊字符和空格
                clean_name = ''.join(e for e in eng_name if e.isalnum() or e in ['.', '_', '-'])
                device['MailAddress'] = f"{clean_name}@compal.com"
            else:
                device['MailAddress'] = ''

        # 收集有效的邮箱地址
        unique_mail_addresses = []
        for item in devicelist:
            mail_addr = item.get('MailAddress', '')
            if mail_addr and '@' in mail_addr and mail_addr not in unique_mail_addresses:
                unique_mail_addresses.append(mail_addr)

        # 添加必要的收件人
        required_recipients = [
            'DQA_LNV_ALL@compal.com',
            'Edwin_Cao@compal.com']
        for recipient in required_recipients:
            if recipient not in unique_mail_addresses:
                unique_mail_addresses.append(recipient)

        print(f"有效的收件人地址: {unique_mail_addresses}")

        # 发送正式邮件
        print("开始发送正式邮件...")
        success = sync_send_email(devicelist, unique_mail_addresses)

        if success:
            print("✓ Email sent successfully!")
        else:
            print("✗ Failed to send email")

    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"Critical error: {str(e)}")
        print(error_msg)

        # 确保日志文件正确关闭
        log_path = r'C:\Send_Emailbug.txt'
        try:
            with open(log_path, 'a+', encoding='utf-8') as f:
                f.write(f"\n\n{'-'*50}\n{datetime.datetime.now()}\n{error_msg}\n")
            print(f"Error logged to {os.path.abspath(log_path)}")
        except Exception as log_error:
            print(f"Failed to write log: {str(log_error)}")