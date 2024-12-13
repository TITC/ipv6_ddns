from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
import json
from .base import BaseDNS

class AliyunDNS(BaseDNS):
    def __init__(self, config):
        super().__init__(config)
        self.aliyun_config = config['aliyun']
        self.client = AcsClient(
            self.aliyun_config['access_key_id'],
            self.aliyun_config['access_key_secret'],
            'cn-hangzhou'
        )
    
    def update_dns_record(self, ipv6):
        try:
            # 查询现有记录
            request = DescribeSubDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_DomainName(self.common_config['domain'])
            request.set_SubDomain(
                f"{self.common_config['subdomain']}.{self.common_config['domain']}"
            )
            request.set_Type("AAAA")
            
            response = self.client.do_action_with_exception(request)
            domain_list = json.loads(response)
            
            if domain_list['TotalCount'] == 0:
                self._add_record(ipv6)
            else:
                current_ip = domain_list['DomainRecords']['Record'][0]['Value'].strip()
                if current_ip != ipv6:
                    self._update_record(
                        domain_list['DomainRecords']['Record'][0]['RecordId'],
                        ipv6
                    )
                    self.send_notification(ipv6, current_ip)
                else:
                    self.logger.info("IPv6地址未变更，无需更新")
                    
        except Exception as e:
            self.logger.error(f"更新DNS记录失败: {str(e)}")
    
    def _add_record(self, ipv6):
        request = AddDomainRecordRequest()
        request.set_accept_format('json')
        request.set_DomainName(self.common_config['domain'])
        request.set_RR(self.common_config['subdomain'])
        request.set_Type("AAAA")
        request.set_Value(ipv6)
        request.set_TTL(self.aliyun_config['ttl'])
        
        self.client.do_action_with_exception(request)
        self.logger.info(f"添加新的DNS记录: {ipv6}")
        self.send_notification(ipv6)
    
    def _update_record(self, record_id, ipv6):
        request = UpdateDomainRecordRequest()
        request.set_accept_format('json')
        request.set_RecordId(record_id)
        request.set_RR(self.common_config['subdomain'])
        request.set_Type("AAAA")
        request.set_Value(ipv6)
        request.set_TTL(self.aliyun_config['ttl'])
        
        self.client.do_action_with_exception(request)
        self.logger.info(f"更新DNS记录: {ipv6}")