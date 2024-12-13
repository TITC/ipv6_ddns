from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from utils.logger import Logger
import socket
import platform
import time

class BaseDNS(ABC):
    def __init__(self, config):
        self.config = config
        self.common_config = config['common']
        self.logger = Logger.get_logger()
        
    @abstractmethod
    def update_dns_record(self, ipv6):
        """更新DNS记录"""
        pass
    
    def send_notification(self, ipv6, old_ipv6=None):
        """发送邮件通知"""
        try:
            # 获取设备信息
            hostname = socket.gethostname()
            os_info = platform.system() + " " + platform.release()
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            # 构建邮件主题
            subject = f"[{hostname}] {self.common_config['subdomain']}.{self.common_config['domain']} IPv6地址变更通知"
            
            # 构建邮件内容
            content = f"""
设备信息:
- 主机名: {hostname}
- 操作系统: {os_info}
- 更新时间: {current_time}

域名信息:
- 完整域名: {self.common_config['subdomain']}.{self.common_config['domain']}
- DNS提供商: {self.__class__.__name__.replace('DNS', '')}

IPv6地址变更:
- 旧地址: {old_ipv6 if old_ipv6 else '新建记录'}
- 新地址: {ipv6}

备注:
- 此邮件由自动DDNS更新服务发送
- 如有异常请检查设备网络配置
            """
            
            msg = MIMEText(content)
            msg["Subject"] = subject
            msg["From"] = self.common_config['sender_email']
            msg["To"] = ";".join(self.common_config['receiver_emails'])
            
            with smtplib.SMTP_SSL(
                self.common_config['mail_host'], 
                465
            ) as server:
                server.login(
                    self.common_config['sender_email'],
                    self.common_config['email_password']
                )
                server.sendmail(
                    self.common_config['sender_email'],
                    self.common_config['receiver_emails'],
                    msg.as_string()
                )
            
            self.logger.info("邮件通知发送成功")
        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {str(e)}") 