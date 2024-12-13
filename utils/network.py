import random
import requests
import subprocess
import socket
from utils.logger import Logger

logger = Logger.get_logger()

def get_ipv6_from_websites(timeout=60):
    """通过外部网站API获取公网IPv6地址"""
    websites = [
        "https://6.ipw.cn",
        "https://ipv6.icanhazip.com",
        "https://api6.ipify.org",
        "https://v6.ident.me"
    ]
    
    # 创建不使用代理的会话
    session = requests.Session()
    session.trust_env = False  # 避免因为代理不支持ipv6导致获取失败
    
    for website in random.sample(websites, len(websites)):
        try:
            response = session.get(website, timeout=timeout, proxies={'http': None, 'https': None})
            if response.status_code == 200:
                ipv6 = response.text.strip()
                logger.info(f"通过网站API获取IPv6地址成功: {ipv6} (来源: {website})")
                return ipv6
        except requests.exceptions.RequestException as e:
            logger.warning(f"从 {website} 获取IPv6地址失败: {str(e)}")
    return None



def get_ipv6_from_interface():
    """通过系统命令获取本地网卡IPv6地址"""
    try:
        if subprocess.os.name == 'nt':  # Windows
            # 使用 PowerShell 命令获取更准确的 IPv6 信息
            cmd = "Get-NetIPAddress -AddressFamily IPv6 | Where-Object { $_.PrefixOrigin -eq 'RouterAdvertisement' } | Select-Object IPAddress"
            output = subprocess.check_output(['powershell', '-Command', cmd], text=True)
            for line in output.split('\n'):
                line = line.strip()
                if line and not line.startswith('IPAddress') and not line.startswith('-') and not line.startswith('fe80'):
                    ipv6 = line.strip()
                    logger.info(f"通过Windows网卡获取IPv6地址成功: {ipv6}")
                    return ipv6
        else:  # Linux/Unix
            # 使用 ip 命令获取 IPv6 地址，排除临时地址和链路本地地址
            cmd = "ip -6 addr show scope global | grep -v temporary | grep inet6 | awk '{print $2}' | cut -d'/' -f1"
            output = subprocess.check_output(cmd, shell=True, text=True)
            for line in output.split('\n'):
                line = line.strip()
                if line and not line.startswith('fe80'):
                    ipv6 = line
                    logger.info(f"通过Linux网卡获取IPv6地址成功: {ipv6}")
                    return ipv6
    except Exception as e:
        logger.warning(f"通过网卡获取IPv6地址失败: {str(e)}")
    return None

def get_ipv6_from_dns():
    """通过DNS解析获取IPv6地址"""
    try:
        # 创建IPv6套接字并连接到谷歌DNS
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.connect(('2001:4860:4860::8888', 53))
        ipv6 = sock.getsockname()[0]
        sock.close()
        if ipv6 and not ipv6.startswith('fe80'):
            logger.info(f"通过DNS解析获取IPv6地址成功: {ipv6}")
            return ipv6
    except Exception as e:
        logger.warning(f"通过DNS解析获取IPv6地址失败: {str(e)}")
    return None

def get_ipv6(timeout=60):
    """获取当前公网IPv6地址，按优先级尝试不同方法"""
    # 按优先级尝试不同的获取方法
    methods = [
        get_ipv6_from_websites,
        get_ipv6_from_interface,
        get_ipv6_from_dns
    ]
    
    for method in methods:
        try:
            if method == get_ipv6_from_websites:
                result = method(timeout)
            else:
                result = method()
            if result:
                return result
        except Exception as e:
            logger.warning(f"使用{method.__name__}获取IPv6地址时发生错误: {str(e)}")
            continue
    
    logger.error("所有获取IPv6地址的方法都失败了")
    return None