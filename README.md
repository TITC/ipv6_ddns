# IPv6 DDNS 更新工具

这是一个用于自动更新域名 IPv6 AAAA 记录的 DDNS 工具。支持阿里云 DNS 和 Cloudflare DNS 服务。

## 功能特点

- 自动获取本机公网 IPv6 地址
- 支持阿里云 DNS 和 Cloudflare DNS 服务
- 定时检查 IPv6 地址变化并更新 DNS 记录
- IPv6 地址变更时发送邮件通知
- 支持多个接收邮箱
- 详细的日志记录
- 支持系统服务自启动

## 配置说明

配置文件为 `config.yaml`，包含以下配置项：

### 通用配置
- receiver_emails: 接收通知的邮箱列表
- sender_email: 发送通知的邮箱账号
- mail_host: 邮件服务器地址
- email_password: 邮箱授权码
- subdomain: 需要更新的子域名
- domain: 主域名
- check_interval: 检查 IP 变化的时间间隔(秒)
- ipv6_timeout: IPv6 地址获取超时时间(秒)

### 阿里云配置
- enabled: 是否启用阿里云 DNS 更新
- access_key_id: 阿里云访问密钥 ID
- access_key_secret: 阿里云访问密钥密码
- ttl: DNS 记录的 TTL 值(600-86400秒)

### Cloudflare 配置
- enabled: 是否启用 Cloudflare DNS 更新
- cloudflare_token: Cloudflare API 令牌
- zone_id: Cloudflare 区域 ID
- ttl: DNS 记录的 TTL 值(秒)

## 使用方法

1. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

2. 修改配置文件:
   - 复制 `config.yaml.example` 为 `config.yaml`
   - 根据实际情况修改配置项

3. 运行程序:
   ```bash
   python main.py
   ```

4. 运行测试:

   运行单个测试:
   ```bash
   pytest tests/test_network.py::test_get_ipv6_from_websites -v
   ```

   显示详细输出:
   ```bash
   pytest tests/test_network.py -v -s
   ```

   显示测试进度:
   ```bash
   pytest tests/test_network.py -v --tb=short --maxfail=1
   ```

5. 设置为系统服务:

   创建服务文件:
   ```bash
   sudo vim /etc/systemd/system/ipv6-ddns.service
   ```

   添加以下内容:
   ```ini
   [Unit]
   Description=IPv6 DDNS Update Service
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/path/to/ipv6_ddns
   ExecStart=/usr/bin/python3 /path/to/ipv6_ddns/main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   启用并启动服务:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ipv6-ddns
   sudo systemctl start ipv6-ddns
   ```

   查看服务状态:
   ```bash
   sudo systemctl status ipv6-ddns
   ```
