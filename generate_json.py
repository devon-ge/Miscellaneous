import math
import json
import urllib.request

url = "http://ftp.apnic.net/stats/apnic/delegated-apnic-latest"
cidrs = []

# 1. 抓取 APNIC 日志
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    for line in response:
        line = line.decode("utf-8").strip()
        parts = line.split("|")

        # 提取 Country Code 为 CN 且状态为已分配的记录
        if len(parts) >= 7 and parts[1] == "CN" and parts[6] in ("allocated", "assigned"):
            ip_type = parts[2]
            start_ip = parts[3]
            value = int(parts[4])

            if ip_type == "ipv4":
                prefix = 32 - int(math.log2(value))
                cidrs.append(f"{start_ip}/{prefix}")
            elif ip_type == "ipv6":
                cidrs.append(f"{start_ip}/{value}")

# 2. 构造 Sing-Box Source JSON 格式
singbox_rule = {
    "version": 1,
    "rules": [
        {
            "ip_cidr": cidrs
        }
    ]
}

# 3. 输出为 apnic_cn.json
with open("apnic_cn.json", "w", encoding="utf-8") as f:
    json.dump(singbox_rule, f, indent=2)

print(f"成功导出 {len(cidrs)} 条 APNIC CN CIDR 到 apnic_cn.json")
