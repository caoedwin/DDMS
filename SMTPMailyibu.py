import requests
import io
import asyncio
import traceback
from aiosmtplib import SMTP, SMTPException
from datetime import date
import datetime,os, json
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

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

async def test_smtp(devicelist, email_list):
    msg = MIMEMultipart()

    user_name = 'DDMS@Compal.com;'
    msg['From'] = user_name
    msg['To'] = ";".join(email_list)  # 用逗号连接列表元素
    msg['Cc'] = 'DQA_LNV_Managers@compal.com'
    # msg['Cc'] = 'Edwin_Cao@compal.com'
    msg['Subject'] = '【APDQA設備超期提醒】'
    # 添加邮件正文
    # print(devicelist,'devicelist')
    # print(msg['To'], msg['Cc'], "msg['To'], msg['Cc']")
    if len(devicelist) == 0:
        body = MIMEText("""
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
                    """.format(len(devicelist)), "html", "utf-8")
    else:
        body = MIMEText("""
            <html>
                <body>
                    
                    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                        
                        <p>Dear all,</p>
                        <p style="color: #d9534f; font-weight: bold;">
                            你有設備超期！！！請立即預約歸還！！！
                        </p>
                        <h2>设备报告数据</h2>
                        <p>附件是完整的设备报告数据，请查收。</p>
                        <p>此邮件包含 {} 条设备记录。</p>
                        
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
            """.format(len(devicelist)), "html", "utf-8")
    msg.attach(body)

    # mail附件
    excel_data = create_excel_in_memory(devicelist)
    attachment = MIMEApplication(excel_data, Name="设备报告.xlsx")
    attachment['Content-Disposition'] = f'attachment; filename="设备报告.xlsx"'
    msg.attach(attachment)

    try:
        print('Ready to send E-Mail')
        async with SMTP(hostname='10.128.2.181', port=25, use_tls=False, timeout=10, validate_certs=True) as smtp:
            print('Start send E-Mail')
            await smtp.send_message(msg)
            print('Send E-Mail Success')
            await smtp.quit()
            smtp.close()
            print('SMTP connect close')
            return True
    except BaseException as e:
        print("Failed to send email: ")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        Devicelist = ImportDeviceInfo(BrwStatus='已借出')
        Num = 7 #超过多少天提醒
        today = date.today()
        devicelist = [dict(item, OverDay=(today - date.fromisoformat(item["Plandate"])).days)
                  for item in Devicelist
                  if (today - date.fromisoformat(item["Plandate"])).days >= Num]
        # print(result)
        Pers_list = ImportPersonalInfo(Customer='')
        group_info_map = {
            p['GroupNum']: (p['DepartmentCode'], p['EngName'])
            for p in Pers_list if p.get('GroupNum')
        }


        for device in devicelist:
            device['Department'] = group_info_map.get(device.get('Usrname', ''), '')
            group_key = device.get('Usrname', '')

            # 获取部门代码和英文名
            dept_code, eng_name = group_info_map.get(group_key, ('', ''))

            # 添加部门字段
            device['Department'] = dept_code if dept_code else '人员信息系统里面没有此人部门代码信息'

            # 添加邮箱字段（如果英文名存在）
            if eng_name:
                # 清理英文名中的特殊字符和空格
                clean_name = ''.join(e for e in eng_name if e.isalnum() or e in ['.', '_'])
                device['MailAddress'] = f"{clean_name}@compal.com"
            else:
                device['MailAddress'] = '人员信息系统里面没有此人英文名信息'
        # print(devicelist)
        unique_mail_addresses = list({item['MailAddress'] for item in devicelist})
        if len(unique_mail_addresses) == 0:
            unique_mail_addresses.append('DQA_LNV_Managers@compal.com')
        asyncio.run(test_smtp(devicelist, unique_mail_addresses))
        # print(unique_mail_addresses)
    except BaseException as e:
        error_msg = traceback.format_exc()
        print(f"Critical error: {str(e)}")

        # 确保日志文件正确关闭
        log_path = r'C:\Send_Emailbug.txt'
        try:
            with open(log_path, 'a+') as f:
                f.write(f"\n\n{'-'*50}\n{error_msg}\n")
            print(f"Error logged to {os.path.abspath(log_path)}")
        except Exception as log_error:
            print(f"Failed to write log: {str(log_error)}")

