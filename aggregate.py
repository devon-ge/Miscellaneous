#!/usr/bin/env python3
"""聚合多源中国大陆 IP 数据，生成 sing-box rule-set JSON 文件。"""

import ipaddress
import json
import os
import re
import sys
import urllib.request
import urllib.error
from typing import List, Set, Tuple

# === 数据源配置 ===
SOURCES = {
    "apnic": {
        "url": "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest",
        "type": "apnic",
    },
    "17mon": {
        "url": "https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt",
        "type": "cidr",
    },
    "china-operator-ipv4": {
        "url": "https://raw.githubusercontent.com/gaoyifan/china-operator-ip/ip-lists/china.txt",
        "type": "cidr",
    },
    "china-operator-ipv6": {
        "url": "https://raw.githubusercontent.com/gaoyifan/china-operator-ip/ip-lists/china6.txt",
        "type": "cidr",
    },
    "asn-china-ipv4": {
        "url": "https://raw.githubusercontent.com/missuo/ASN-China/main/IP.China.ipv4",
        "type": "cidr",
    },
    "asn-china-ipv6": {
        "url": "https://raw.githubusercontent.com/missuo/ASN-China/main/IP.China.ipv6",
        "type": "cidr",
    },
}

OUTPUT_DIR = "output"


def fetch_url(url: str) -> str:
    """下载 URL 内容，返回文本。"""
    print(f"  Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "geoip-cn-aggregator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        print(f"  WARNING: Failed to fetch {url}: {e}", file=sys.stderr)
        return ""


def parse_apnic(text: str) -> List[str]:
    """从 APNIC delegated 文件中提取中国 IPv4 和 IPv6 的 CIDR。"""
    cidrs = []
    for line in text.splitlines():
        if line.startswith("#") or "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) < 5:
            continue
        registry, cc, ip_type, start, count = parts[0], parts[1], parts[2], parts[3], parts[4]
        if cc != "CN":
            continue
        if ip_type == "ipv4":
            try:
                count_int = int(count)
                # APNIC 用主机数表示大小，转换为前缀长度
                import math
                prefix_len = 32 - int(math.log2(count_int))
                cidrs.append(f"{start}/{prefix_len}")
            except (ValueError, ZeroDivisionError):
                continue
        elif ip_type == "ipv6":
            try:
                prefix_len = int(count)
                cidrs.append(f"{start}/{prefix_len}")
            except ValueError:
                continue
    return cidrs


def parse_cidr_list(text: str) -> List[str]:
    """从纯文本 CIDR 列表中提取有效行。"""
    cidrs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # 验证是否为有效 CIDR
        try:
            ipaddress.ip_network(line, strict=False)
            cidrs.append(line)
        except ValueError:
            continue
    return cidrs


def aggregate_cidrs(cidr_list: List[str]) -> Tuple[List[str], List[str]]:
    """聚合 CIDR 列表，合并重叠和相邻网段，分别返回 IPv4 和 IPv6。"""
    ipv4_nets: Set[ipaddress.IPv4Network] = set()
    ipv6_nets: Set[ipaddress.IPv6Network] = set()

    for cidr in cidr_list:
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            if isinstance(net, ipaddress.IPv4Network):
                ipv4_nets.add(net)
            else:
                ipv6_nets.add(net)
        except ValueError:
            continue

    # collapse_addresses 会自动合并重叠和相邻网段
    ipv4_collapsed = sorted(ipaddress.collapse_addresses(ipv4_nets))
    ipv6_collapsed = sorted(ipaddress.collapse_addresses(ipv6_nets))

    ipv4_result = [str(n) for n in ipv4_collapsed]
    ipv6_result = [str(n) for n in ipv6_collapsed]

    return ipv4_result, ipv6_result


def generate_singbox_ruleset(ipv4_list: List[str], ipv6_list: List[str]) -> dict:
    """生成 sing-box rule-set JSON 格式。"""
    return {
        "version": 2,
        "rules": [
            {
                "ip_cidr": ipv4_list + ipv6_list
            }
        ]
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_cidrs: List[str] = []
    total_raw = 0

    for name, source in SOURCES.items():
        print(f"[{name}] Downloading...")
        text = fetch_url(source["url"])
        if not text:
            print(f"[{name}] Skipped (empty response)")
            continue

        if source["type"] == "apnic":
            cidrs = parse_apnic(text)
        else:
            cidrs = parse_cidr_list(text)

        print(f"[{name}] Got {len(cidrs)} CIDRs")
        total_raw += len(cidrs)
        all_cidrs.extend(cidrs)

    print(f"\nTotal raw CIDRs: {total_raw}")
    print("Aggregating and merging...")

    ipv4_list, ipv6_list = aggregate_cidrs(all_cidrs)

    print(f"After merge: IPv4 = {len(ipv4_list)}, IPv6 = {len(ipv6_list)}")
    print(f"Total: {len(ipv4_list) + len(ipv6_list)} CIDRs")

    # 写入纯文本 CIDR 列表
    ipv4_path = os.path.join(OUTPUT_DIR, "cn_ipv4.txt")
    with open(ipv4_path, "w") as f:
        f.write("\n".join(ipv4_list) + "\n")
    print(f"Written: {ipv4_path}")

    ipv6_path = os.path.join(OUTPUT_DIR, "cn_ipv6.txt")
    with open(ipv6_path, "w") as f:
        f.write("\n".join(ipv6_list) + "\n")
    print(f"Written: {ipv6_path}")

    # 生成 sing-box rule-set JSON
    ruleset = generate_singbox_ruleset(ipv4_list, ipv6_list)
    json_path = os.path.join(OUTPUT_DIR, "geoip-cn.json")
    with open(json_path, "w") as f:
        json.dump(ruleset, f, indent=2)
    print(f"Written: {json_path}")

    print("\nDone! Next step: sing-box rule-set compile")


if __name__ == "__main__":
    main()
