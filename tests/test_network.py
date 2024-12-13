import pytest
from utils.network import (
    get_ipv6_from_websites,
    get_ipv6_from_interface,
    get_ipv6_from_dns,
    get_ipv6
)

def is_valid_ipv6(ip):
    """验证是否为有效的IPv6地址"""
    if not ip:
        return False
    # 排除链路本地地址
    if ip.startswith('fe80'):
        return False
    try:
        # 尝试将地址字符串转换为二进制格式来验证
        parts = ip.split(':')
        if len(parts) > 8:
            return False
        return all(0 <= int(part, 16) <= 0xffff for part in parts if part)
    except ValueError:
        return False

def test_get_ipv6_from_websites():
    """测试通过网站API获取IPv6地址"""
    ip = get_ipv6_from_websites(timeout=10)
    assert ip is None or is_valid_ipv6(ip)

def test_get_ipv6_from_interface():
    """测试通过网卡获取IPv6地址"""
    ip = get_ipv6_from_interface()
    assert ip is None or is_valid_ipv6(ip)

def test_get_ipv6_from_dns():
    """测试通过DNS获取IPv6地址"""
    ip = get_ipv6_from_dns()
    assert ip is None or is_valid_ipv6(ip)

def test_get_ipv6():
    """测试整体获取IPv6地址功能"""
    ip = get_ipv6(timeout=10)
    assert ip is None or is_valid_ipv6(ip)

def test_ipv6_format():
    """测试IPv6地址格式验证函数"""
    assert is_valid_ipv6('2001:db8::1')
    assert is_valid_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
    assert not is_valid_ipv6('fe80::1')
    assert not is_valid_ipv6('256.256.256.256')
    assert not is_valid_ipv6('invalid')
    assert not is_valid_ipv6('')
    assert not is_valid_ipv6(None)

@pytest.mark.parametrize("method", [
    get_ipv6_from_websites,
    get_ipv6_from_interface,
    get_ipv6_from_dns
])
def test_all_methods(method):
    """参数化测试所有获取IPv6的方法"""
    if method == get_ipv6_from_websites:
        ip = method(timeout=10)
    else:
        ip = method()
    print(f"Method {method.__name__} returned: {ip}")
    assert ip is None or is_valid_ipv6(ip) 