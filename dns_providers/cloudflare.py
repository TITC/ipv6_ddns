import requests
from .base import BaseDNS

class CloudflareDNS(BaseDNS):
    def __init__(self, config):
        super().__init__(config)
        self.cloudflare_config = config['cloudflare']
        self.headers = {
            'Authorization': f'Bearer {self.cloudflare_config["cloudflare_token"]}',
            'Content-Type': 'application/json'
        }
        
    def update_dns_record(self, ipv6):
        try:
            url = f"https://api.cloudflare.com/client/v4/zones/{self.cloudflare_config['zone_id']}/dns_records"
            
            # 查询现有记录
            params = {
                'name': f"{self.common_config['subdomain']}.{self.common_config['domain']}",
                'type': 'AAAA'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['success']:
                raise Exception(f"API请求失败: {data['errors']}")
            
            if len(data['result']) == 0:
                self._add_record(url, ipv6)
            else:
                current_record = data['result'][0]
                if current_record['content'] != ipv6:
                    self._update_record(url, current_record['id'], ipv6)
                    self.send_notification(ipv6, current_record['content'])
                else:
                    self.logger.info("IPv6地址未变更，无需更新")
                    
        except Exception as e:
            self.logger.error(f"更新DNS记录失败: {str(e)}")
    
    def _add_record(self, url, ipv6):
        """添加新的DNS记录"""
        data = {
            'type': 'AAAA',
            'name': f"{self.common_config['subdomain']}.{self.common_config['domain']}",
            'content': ipv6,
            'ttl': self.cloudflare_config['ttl']
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result['success']:
            self.logger.info(f"添加新的DNS记录: {ipv6}")
            self.send_notification(ipv6)
        else:
            raise Exception(f"添加记录失败: {result['errors']}")
    
    def _update_record(self, url, record_id, ipv6):
        """更新已存在的DNS记录"""
        update_url = f"{url}/{record_id}"
        data = {
            'type': 'AAAA',
            'name': f"{self.common_config['subdomain']}.{self.common_config['domain']}",
            'content': ipv6,
            'ttl': self.cloudflare_config['ttl']
        }
        
        response = requests.put(update_url, headers=self.headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result['success']:
            self.logger.info(f"更新DNS记录: {ipv6}")
        else:
            raise Exception(f"更新记录失败: {result['errors']}") 