# -*- coding: utf-8 -*-
import requests
import json
import time

# 配置参数
DNSpod_API_ID = "DNSPod API ID" # 替换为你的 DNSPod API ID
DNSpod_API_TOKEN = "DNSPod API Token" # 替换为你的 DNSPod API Token
DNSpod_DOMAIN = "darklotus.cn"# 替换为你的 DNSPod 域名
DNSpod_SUB_DOMAIN = "23333"  # 需要更新的子域名
DNSpod_RECORD_TYPE = "A"  # 选择记录类型 "A" 或 "CNAME"
DNSpod_RECORD_LINE = "默认"  # 记录线路
API_ENDPOINT = "https://dnsapi.cn"
MAX_A_RECORDS = 2  # DNSPod 默认线路最多允许的 A 记录数
MAX_CNAME_RECORDS = 1  # DNSPod 默认线路最多允许的 CNAME 记录数

# DDNS 的 IP 地址直接在脚本中定义，以多行文本方式
IP_ADDRESSES = """
127.0.0.1
10.0.0.100
"""  # 示例 IP 地址，请替换为实际的 IP

# DDNS 的 CNAME 值直接在脚本中定义，以多行文本方式
CNAME_VALUE = """
example.com
"""  # 示例 CNAME 值，请替换为实际的 CNAME

# 公共方法
def api_request(api_name, data):
    """发送 POST 请求到 DNSPod API"""
    url = f"{API_ENDPOINT}/{api_name}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "DNSPod-DDNS/1.0.0 (darklotus.cn)"
    }
    data.update({"login_token": f"{DNSpod_API_ID},{DNSpod_API_TOKEN}", "format": "json"})
    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return None
    return response.json()

def get_current_records():
    """获取当前子域名的解析记录"""
    print(f"正在获取子域名 {DNSpod_SUB_DOMAIN}.{DNSpod_DOMAIN} 的解析记录...")
    data = {
        "domain": DNSpod_DOMAIN,
        "sub_domain": DNSpod_SUB_DOMAIN,
    }
    response = api_request("Record.List", data)
    if response and response.get("status", {}).get("code") == "1":
        records = response.get("records", [])
        return records
    else:
        print(f"获取解析记录失败：{response}")
        return []

def update_record(record_id, record_type, value):
    """更新已有解析记录，支持重试机制。"""
    attempt = 0  # 当前尝试次数
    max_retries = 3
    retry_delay = 5

    while attempt < max_retries:
        try:
            print(f"正在更新记录 ID {record_id} 为 {record_type} 值 {value}（尝试 {attempt + 1}/{max_retries}）...")
            data = {
                "domain": DNSpod_DOMAIN,
                "record_id": record_id,
                "sub_domain": DNSpod_SUB_DOMAIN,
                "record_type": record_type,
                "record_line": DNSpod_RECORD_LINE,
                "value": value
            }
            response = api_request("Record.Modify", data)

            if response and response.get("status", {}).get("code") == "1":
                print(f"记录更新成功：{response}")
                return  # 成功时退出函数
            else:
                print(f"记录更新失败：{response}")
                if response.get("status", {}).get("code") == "104":
                    print("记录已经存在，无需再次添加。")
                    return  # 如果记录已经存在，不再重试
        except Exception as e:
            print(f"更新记录时发生错误：{e}")

        # 如果未成功，等待一段时间后重试
        attempt += 1
        if attempt < max_retries:
            print(f"更新失败，等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)
    
    print(f"多次尝试后仍无法更新记录 ID {record_id}，请检查网络或 API 配置。")

def create_record(record_type, value):
    """创建新的解析记录"""
    print(f"正在创建新记录 {record_type} 值 {value}...")
    data = {
        "domain": DNSpod_DOMAIN,
        "sub_domain": DNSpod_SUB_DOMAIN,
        "record_type": record_type,
        "record_line": DNSpod_RECORD_LINE,
        "value": value
    }
    response = api_request("Record.Create", data)
    if response and response.get("status", {}).get("code") == "1":
        print(f"记录创建成功：{response}")
    else:
        print(f"记录创建失败：{response}")

def delete_record(record_id):
    """删除解析记录"""
    print(f"正在删除记录 ID {record_id}...")
    data = {
        "domain": DNSpod_DOMAIN,
        "record_id": record_id
    }
    response = api_request("Record.Remove", data)
    if response and response.get("status", {}).get("code") == "1":
        print(f"记录删除成功：{response}")
    else:
        print(f"记录删除失败：{response}")

# 主逻辑
def main():
    current_records = get_current_records()

    # 处理 IP_ADDRESSES
    ip_addresses = [ip.strip() for ip in IP_ADDRESSES.splitlines() if ip.strip()]

    # 处理 CNAME_VALUE
    cname_values = [cname.strip() for cname in CNAME_VALUE.splitlines() if cname.strip()]

    if DNSpod_RECORD_TYPE == "A":
        if not ip_addresses:
            print("没有定义有效的 IP 地址，脚本退出。")
            return

        # 删除所有现有的 CNAME 记录
        cname_records = [r for r in current_records if r["type"] == "CNAME"]
        for record in cname_records:
            delete_record(record["id"])

        a_records = [r for r in current_records if r["type"] == "A"]
        existing_ips = {record["value"]: record for record in a_records}

        # 输出当前解析记录的 IP 地址
        current_ip_values = [record["value"] for record in a_records]
        print(f"当前的解析记录：{current_ip_values}")

        # 输出即将 DDNS 的 IP 地址
        print(f"即将DDNS的IP：{ip_addresses[:10]}")  # 只显示前10个IP

        # 确保只处理最多 MAX_A_RECORDS 个 IP
        ip_addresses = ip_addresses[:MAX_A_RECORDS]

        # 遍历即将更新的 IP 地址
        for ip_address in ip_addresses:
            if ip_address in existing_ips:
                print(f"IP：{ip_address} 记录已经存在，无需再次添加。")
            else:
                # 如果有现有的记录可以更新，则更新它
                if a_records:
                    record = a_records.pop(0)  # 从现有记录中移除
                    print(f"正在更新IP：{ip_address}，将替换记录 {record['value']}（ID：{record['id']}）...")
                    update_record(record["id"], "A", ip_address)
                else:
                    # 如果没有现有的记录可以更新，则创建新的记录
                    create_record("A", ip_address)

    elif DNSpod_RECORD_TYPE == "CNAME":
        if not cname_values:
            print("没有定义有效的 CNAME 值，脚本退出。")
            return

        # 删除所有现有的 A 记录
        a_records = [r for r in current_records if r["type"] == "A"]
        for record in a_records:
            delete_record(record["id"])

        # 处理 CNAME 记录
        cname_records = [r for r in current_records if r["type"] == "CNAME"]
        
        # 确保只处理一个 CNAME 值
        cname_value = cname_values[:MAX_CNAME_RECORDS]

        if len(cname_records) > 0:
            # 更新现有的 CNAME 记录
            for record in cname_records[:MAX_CNAME_RECORDS]:
                update_record(record["id"], "CNAME", cname_value[0])
            # 删除多余的 CNAME 记录
            for record in cname_records[MAX_CNAME_RECORDS:]:
                delete_record(record["id"])
        else:
            # 创建新的 CNAME 记录
            create_record("CNAME", cname_value[0])

    else:
        print("未知的记录类型，请指定 'A' 或 'CNAME'。")
        return

    # 只打印更新后的解析记录值，不再获取和打印当前解析记录
    if DNSpod_RECORD_TYPE == "A":
        print(f"脚本执行完成，更新后的解析记录值: {ip_addresses[:MAX_A_RECORDS]}")
    else:
        print(f"脚本执行完成，更新后的解析记录值: {cname_value[:MAX_CNAME_RECORDS]}")

if __name__ == "__main__":
    main()