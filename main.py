import os
import time
import yaml
from utils.logger import Logger
from utils.network import get_ipv6
from dns_providers.aliyun import AliyunDNS
from dns_providers.cloudflare import CloudflareDNS


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


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
