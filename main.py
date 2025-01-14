import os
import time
import yaml
from utils.logger import Logger
from utils.network import get_ipv6
from dns_providers.aliyun import AliyunDNS
from dns_providers.cloudflare import CloudflareDNS


def get_interactive_config():
    """通过交互方式获取必要的配置"""
    config = {
        'common': {},
        'aliyun': {'enabled': False},
        'cloudflare': {'enabled': False}
    }
    
    print("\n=== 基础配置 ===")
    config['common']['subdomain'] = input("请输入子域名: ").strip()
    config['common']['domain'] = input("请输入主域名: ").strip()
    config['common']['check_interval'] = int(input("请输入检查间隔(秒)[默认3600]: ").strip() or "3600")
    config['common']['ipv6_timeout'] = int(input("请输入IPv6超时时间(秒)[默认60]: ").strip() or "60")

    print("\n=== DNS服务商配置 ===")
    # Aliyun配置
    if input("是否启用阿里云DNS? (y/N): ").lower().strip() == 'y':
        config['aliyun']['enabled'] = True
        config['aliyun']['access_key_id'] = input("请输入阿里云AccessKey ID: ").strip()
        config['aliyun']['access_key_secret'] = input("请输入阿里云AccessKey Secret: ").strip()
        config['aliyun']['ttl'] = int(input("请输入TTL值(600-86400)[默认600]: ").strip() or "600")

    # Cloudflare配置
    if input("是否启用Cloudflare DNS? (y/N): ").lower().strip() == 'y':
        config['cloudflare']['enabled'] = True
        config['cloudflare']['cloudflare_token'] = input("请输入Cloudflare API Token: ").strip()
        config['cloudflare']['zone_id'] = input("请输入Cloudflare Zone ID: ").strip()
        config['cloudflare']['ttl'] = int(input("请输入TTL值[默认120]: ").strip() or "120")

    return config


def load_config():
    """尝试从文件加载配置，如果失败则使用交互式配置"""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"配置文件读取失败: {str(e)}")
        print("切换到交互式配置模式...")
        return get_interactive_config()


def main():
    logger = Logger.get_logger()
    config = load_config()

    dns_providers = []

    # 初始化启用的DNS服务提供商
    if config['aliyun']['enabled']:
        dns_providers.append(AliyunDNS(config))
    if config['cloudflare']['enabled']:
        dns_providers.append(CloudflareDNS(config))

    if not dns_providers:
        logger.warning("没有启用任何DNS服务提供商")
        return

    while True:
        try:
            ipv6 = get_ipv6(config['common']['ipv6_timeout'])
            if ipv6:
                for provider in dns_providers:
                    provider.update_dns_record(ipv6)
            else:
                logger.error("无法获取IPv6地址")

        except Exception as e:
            logger.error(f"运行时错误: {str(e)}")

        time.sleep(config['common']['check_interval'])


if __name__ == "__main__":
    main()
