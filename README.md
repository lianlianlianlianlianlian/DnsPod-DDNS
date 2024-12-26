# DNSPod DDNS (动态DNS) 脚本

此脚本用于通过 DNSPod API 自动更新 DNS 记录，支持 A 记录和 CNAME 记录的动态更新。可以在本地或服务器环境中运行，适用于需要自动化管理 DNS 解析的场景。

## 功能概述

- **支持 A 记录和 CNAME 记录的更新**。
- **自动删除旧的 DNS 记录**，避免记录冗余。
- **支持自动创建新的解析记录**，如果没有找到对应的记录。
- **重试机制**，确保在网络或 API 错误时可以自动重试。
- **自定义 DDNS IP 地址**，可以通过修改脚本中的 `IP_ADDRESSES` 列表来指定需要更新的 IP 地址。

## 配置要求

1. **Python 3.x**：本脚本需要 Python 3.x 环境。
2. **requests 库**：用于发送 HTTP 请求。可以通过以下命令安装：
   ```bash
   pip install requests
   ```
3. **DNSPod API Token**：脚本需要你的 DNSPod API ID 和 API Token，获取方式如下：
   - 登录到 [DNSPod](https://www.dnspod.cn/)，进入控制台，创建一个 API Token。
   - 将 Token 填入脚本中的 `DNSpod_API_ID` 和 `DNSpod_API_TOKEN`。

## 使用方法

### 1. 配置参数

在脚本中，找到以下配置项，并根据你的实际情况进行修改：

```python
DNSpod_API_ID = "DNSPod API ID"  # 替换为你的 DNSPod API ID
DNSpod_API_TOKEN = "DNSPod API Token"  # 替换为你的 DNSPod API Token
DNSpod_DOMAIN = "darklotus.cn"  # 替换为你的 DNSPod 域名
DNSpod_SUB_DOMAIN = "23333"  # 替换为你需要更新的子域名
DNSpod_RECORD_TYPE = "A"  # 选择记录类型："A" 或 "CNAME"
DNSpod_RECORD_LINE = "默认"  # 选择记录线路，通常是 "默认"
API_ENDPOINT = "https://dnsapi.cn"  # DNSPod API 地址
MAX_A_RECORDS = 2  # DNSPod 默认线路最多允许的 A 记录数
MAX_CNAME_RECORDS = 1  # DNSPod 默认线路最多允许的 CNAME 记录数
```

- `IP_ADDRESSES`：定义你要更新的 IP 地址列表。如果是 A 记录，脚本会根据这些 IP 地址进行动态更新。
- `CNAME_VALUE`：如果你使用 CNAME 记录，定义相应的 CNAME 值。

### 2. 运行脚本

配置完成后，直接运行脚本：

```bash
python3 ddns.py
```

### 3. 脚本工作流程

- **获取当前解析记录**：脚本会从 DNSPod API 获取当前子域名的解析记录。
- **更新 A 记录**：如果记录类型为 A，脚本会检查是否有现有的记录。如果有，更新这些记录；如果没有，创建新的记录。
- **更新 CNAME 记录**：如果记录类型为 CNAME，脚本会删除所有现有的 A 记录，并创建或更新 CNAME 记录。
- **重试机制**：如果请求失败，脚本会最多重试 3 次，每次重试之间有 5 秒的延迟。

### 4. 支持的记录类型

- **A 记录**：使用 IP 地址更新。
- **CNAME 记录**：使用域名别名（CNAME）更新。

## 常见问题

### 1. DNSPod API 限制

DNSPod 默认每个账户的 API 每天有一定的请求次数限制。请确保脚本的运行频率不超过该限制。

### 2. 如何修改 IP 地址？

在脚本中修改 `IP_ADDRESSES` 列表，添加你需要的 IP 地址即可。请确保 IP 地址符合你的需求，并与实际设备的 IP 地址保持同步。

```python
IP_ADDRESSES = [
    "192.168.1.1",
    "10.0.0.1"
]
```

### 3. 如何设置定时任务？

你可以使用 cron 或类似的任务调度工具，定时执行该脚本以自动更新 DNS 记录。

#### Linux/macOS 使用 cron 设置定时任务：

```bash
crontab -e
```

然后添加一行，设置每天凌晨 3 点运行脚本：

```
0 3 * * * python /path/to/ddns.py
```

### 4. 如何检查 DNS 更新是否成功？

你可以使用以下命令检查 DNS 解析是否已更新：

```bash
nslookup 23333.darklotus.cn
```

或者使用在线 DNS 工具检查解析记录。

## 贡献

如果你有改进建议或发现问题，欢迎提交 Issues 或 Pull Requests。

## 许可证

该项目遵循 MIT 许可证。详情请见 [LICENSE](LICENSE)。

---

### 说明

- 本 README 文件包含了脚本的基本功能介绍、配置说明、使用方法以及常见问题的解答。
- 可以根据需要修改和定制脚本的功能。
- 如果你需要定期自动更新 DNS 记录，建议结合 cron 或其他调度工具进行定时执行。

希望这篇 README 对你有所帮助！如果有更多问题，随时可以提问！