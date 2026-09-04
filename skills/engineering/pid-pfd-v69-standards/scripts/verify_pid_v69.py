#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v6.9 P&ID 自动化验证脚本

根据 references/checklist.md 逐项 grep 检查 P&ID 文件,验证 18 条铁律 + 5 个历史错误避免项。

用法: python3 verify_pid_v69.py <pid_file.html>
退出码: 0=全部通过, 1=有失败项
"""

import sys
import re
import os

# 18 条铁律 + 5 个历史错误项的 grep 检查
CHECKS = [
    # ===== A. 主管与公用工程 (4) =====
    {
        "id": "A1-N2-主管-不延伸",
        "desc": "N₂ 主管 y=60-100 (V-101/V-102/V-103) 段存在",
        "pattern": r'<line\s+x1="\d+"\s+y1="60"\s+x2="\d+"\s+y2="100"',
        "min_count": 1,
        "severity": "warn",
    },
    {
        "id": "A4-XV301-N2-主管中点",
        "desc": "XV-301 在 N₂ 主管中点 (1280, 230)",
        "pattern": r'translate\(1280,230\)',
        "min_count": 1,
        "severity": "error",
    },
    {
        "id": "A4-XV301-旧位置已删",
        "desc": "XV-301 旧位置 (1480, 400) 已删除",
        "pattern": r'translate\(1480,400\)',
        "min_count": 0,
        "severity": "error",
    },
    # ===== B. 阀门 (4) =====
    {
        "id": "B1-LCV201-存在",
        "desc": "LCV-201 阀门符号 (440, 750) 存在",
        "pattern": r'translate\(440,750\)',
        "min_count": 1,
        "severity": "error",
    },
    {
        "id": "B1-阀门在流股中点-数量",
        "desc": "流股中点阀门 (9 个: TCV-301H/301C/201H/401H + LCV-301/201 + PCV-301/201/401)",
        "patterns": [
            r'translate\(220,908\)',  # TCV-301H
            r'translate\(1340,878\)', # TCV-301C
            r'translate\(360,858\)',  # TCV-201H
            r'translate\(1660,858\)', # TCV-401H
            r'translate\(1490,855\)', # LCV-301
            r'translate\(440,750\)',  # LCV-201
            r'translate\(1280,350\)', # PCV-301
            r'translate\(380,360\)',  # PCV-201
            r'translate\(1780,360\)', # PCV-401
        ],
        "min_count": 9,
        "severity": "error",
    },
    {
        "id": "B2-信号线止圈外-TCV301H",
        "desc": "TCV-301H 信号线终点 (208, 887) 止于圈外",
        "pattern": r'x1="220"\s+y1="395"\s+x2="220"\s+y2="887"',
        "min_count": 1,
        "severity": "warn",
    },
    {
        "id": "B2-信号线止圈外-PCV301",
        "desc": "PCV-301 信号线终点 (1268, 329) 止于圈外",
        "pattern": r'x1="1280"\s+y1="350"\s+x2="1280"\s+y2="329"',
        "min_count": 1,
        "severity": "warn",
    },
    {
        "id": "B3-13阀门全标",
        "desc": "13 阀门全标 (Z-102/XV-102/XV-301/FCV-301/PCV-301/LCV-301/TCV-301H/TCV-301C/PSV-301/TCV-201H/LCV-201/PCV-201/TCV-401H/PCV-401)",
        "patterns": [
            r'>\s*Z-102\s*<',
            r'>\s*XV-102\s*<',
            r'>\s*XV-301\s*<',
            r'>\s*FCV-301\s*<',
            r'>\s*PCV-301\s*<',
            r'>\s*LCV-301\s*<',
            r'>\s*TCV-301H\s*<',
            r'>\s*TCV-301C\s*<',
            r'>\s*PSV-301\s*<',
            r'>\s*TCV-201H\s*<',
            r'>\s*LCV-201\s*<',
            r'>\s*PCV-201\s*<',
            r'>\s*TCV-401H\s*<',
            r'>\s*PCV-401\s*<',
        ],
        "min_count": 14,
        "severity": "error",
    },
    # ===== C. 仪表控制 (6) =====
    {
        "id": "C1-正确tap-6条",
        "desc": "正确实线 tap 6 条 (TIRC-201/LRC-201/TIRC-301/LRC-301/AI-301/TIRC-401)",
        "patterns": [
            r'x1="278"\s+y1="450"\s+x2="320"\s+y2="450"',  # TIRC-201
            r'x1="278"\s+y1="490"\s+x2="320"\s+y2="490"',  # LRC-201
            r'x1="920"\s+y1="480"\s+x2="1080"\s+y2="480"',  # TIRC-301
            r'x1="920"\s+y1="580"\s+x2="1080"\s+y2="580"',  # LRC-301
            r'x1="920"\s+y1="680"\s+x2="1080"\s+y2="680"',  # AI-301
            r'x1="1598"\s+y1="500"\s+x2="1620"\s+y2="500"', # TIRC-401
        ],
        "min_count": 6,
        "severity": "error",
    },
    {
        "id": "C1-错误tap-已删-PIRC201",
        "desc": "PIRC-201 错误 tap (278,530)→(320,530) 已删除",
        "pattern": r'x1="278"\s+y1="530"\s+x2="320"\s+y2="530"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C1-错误tap-已删-FRC301",
        "desc": "FRC-301 错误 tap (920,530)→(1080,530) 已删除",
        "pattern": r'x1="920"\s+y1="530"\s+x2="1080"\s+y2="530"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C1-错误tap-已删-PIRC301",
        "desc": "PIRC-301 错误 tap (920,630)→(1080,630) 已删除",
        "pattern": r'x1="920"\s+y1="630"\s+x2="1080"\s+y2="630"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C1-错误tap-已删-PIRC401",
        "desc": "PIRC-401 错误 tap (1598,540)→(1620,540) 已删除",
        "pattern": r'x1="1598"\s+y1="540"\s+x2="1620"\s+y2="540"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C2-虚线控制信号-存在",
        "desc": "虚线控制信号存在 (stroke=#FF6F00 dasharray=4,3)",
        "pattern": r'stroke="#FF6F00"\s+stroke-width="1"\s+stroke-dasharray="4,3"',
        "min_count": 5,
        "severity": "warn",
    },
    {
        "id": "C3-公共竖线已废除-V201",
        "desc": "V-201 旧公共竖线 x=190 已废除",
        "pattern": r'x1="190"\s+y1="340"\s+x2="190"\s+y2="837"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C3-公共竖线已废除-R301",
        "desc": "R-301 旧公共竖线 x=830 已废除",
        "pattern": r'x1="830"\s+y1="340"\s+x2="830"\s+y2="900"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C3-公共竖线已废除-V401",
        "desc": "V-401 旧公共竖线 x=1530 已废除",
        "pattern": r'x1="1530"\s+y1="340"\s+x2="1530"\s+y2="870"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "C4-信号线竖线错开-V201",
        "desc": "V-201 信号线竖线错开 (x=228/236/244)",
        "patterns": [
            r'x1="228".*y2="858"',
            r'x1="236".*y2="750"',
            r'x1="244".*y2="360"',
        ],
        "min_count": 3,
        "severity": "warn",
    },
    {
        "id": "C4-信号线竖线错开-R301",
        "desc": "R-301 信号线竖线错开 (x=842/850/858/866/874)",
        "patterns": [
            r'x1="842".*y2="350"',
            r'x1="850".*y2="887"',
            r'x1="858".*y2="857"',
            r'x1="866".*y2="379"',
            r'x1="874".*y2="849"',
        ],
        "min_count": 5,
        "severity": "warn",
    },
    {
        "id": "C4-信号线竖线错开-V401",
        "desc": "V-401 信号线竖线错开 (x=1552/1556)",
        "patterns": [
            r'x1="1552".*y2="858"',
            r'x1="1556".*y2="360"',
        ],
        "min_count": 2,
        "severity": "warn",
    },
    # ===== D. 旧线段清理 (2) =====
    {
        "id": "D1-旧信号线段已清理-V401",
        "desc": "V-401 旧信号线段 x=1530 已清理",
        "pattern": r'x1="1530"\s+y1="(500|540)"',
        "min_count": 0,
        "severity": "error",
    },
    {
        "id": "D2-XV301-旧位置已删",
        "desc": "XV-301 旧位置 (1480, 400) 已删",
        "pattern": r'translate\(1480,400\)',
        "min_count": 0,
        "severity": "error",
    },
    # ===== E. 伴热 (1) =====
    {
        "id": "E1-无伴热大矩形",
        "desc": "无伴热大填充矩形 (fill=#FFFACD fill-opacity=0.35 stroke=none) [v6.3 整改]",
        "pattern": r'fill="#FFFACD"\s+fill-opacity="0\.35"\s+stroke="none"',
        "min_count": 0,
        "severity": "error",
    },
    # ===== F. 文档 (2) =====
    {
        "id": "F1-v69-标题",
        "desc": "标题栏含 v6.9 出图规范标识",
        "pattern": r'v6\.9',
        "min_count": 1,
        "severity": "warn",
    },
    {
        "id": "F2-UTF8-BOM",
        "desc": "文件含 UTF-8 BOM (Windows 记事本友好)",
        "pattern": r'^\xef\xbb\xbf',
        "min_count": 1,
        "severity": "error",
        "binary_check": True,
    },
]


def verify_pid(filepath):
    """验证 P&ID 文件,返回 (passed, failed, warnings) 列表"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return [], [], []

    with open(filepath, 'rb') as f:
        content_bytes = f.read()

    # UTF-8 BOM 检查
    has_bom = content_bytes.startswith(b'\xef\xbb\xbf')
    if has_bom:
        content = content_bytes[3:].decode('utf-8', errors='replace')
    else:
        content = content_bytes.decode('utf-8', errors='replace')

    passed = []
    failed = []
    warnings = []

    print("=" * 70)
    print(f"P&ID v6.9 验证报告: {filepath}")
    print(f"文件大小: {len(content_bytes):,} bytes")
    print(f"UTF-8 BOM: {'✓' if has_bom else '✗ (缺失!)'}")
    print("=" * 70)

    for check in CHECKS:
        check_id = check["id"]
        desc = check["desc"]
        severity = check.get("severity", "warn")

        # binary 检查 (用于 BOM)
        if check.get("binary_check"):
            actual_count = 1 if has_bom else 0
        else:
            # 单 pattern 或多 pattern
            # 多 pattern 模式: 统计至少匹配 1 次的 pattern 数量 (min_count=期望匹配数)
            if "patterns" in check:
                matched_count = 0
                for pat in check["patterns"]:
                    matches = re.findall(pat, content)
                    if matches:
                        matched_count += 1
                actual_count = matched_count
            else:
                matches = re.findall(check["pattern"], content)
                actual_count = len(matches)

        min_count = check.get("min_count", 1)
        if min_count > 0:
            passed_check = actual_count >= min_count
        else:
            passed_check = actual_count == 0

        if passed_check:
            symbol = "✓"
            passed.append(check_id)
        else:
            symbol = "✗"
            if severity == "error":
                failed.append(check_id)
            else:
                warnings.append(check_id)

        detail = f"{min_count}+" if min_count > 0 else "0"
        print(f"  {symbol} [{check_id}] {desc}")
        print(f"     实际: {actual_count} (要求: {detail}) 严重度: {severity}")

    return passed, failed, warnings


def main():
    if len(sys.argv) < 2:
        print("用法: python3 verify_pid_v69.py <pid_file.html>")
        print("示例: python3 verify_pid_v69.py /path/to/pid-v69.html")
        sys.exit(2)

    filepath = sys.argv[1]
    passed, failed, warnings = verify_pid(filepath)

    print()
    print("=" * 70)
    print("汇总")
    print("=" * 70)
    print(f"  ✓ 通过: {len(passed)} 项")
    print(f"  ✗ 失败: {len(failed)} 项")
    print(f"  ⚠ 警告: {len(warnings)} 项")

    if failed:
        print()
        print("❌ 失败项 (必须修复):")
        for f in failed:
            print(f"  - {f}")

    if warnings:
        print()
        print("⚠ 警告项 (建议修复):")
        for w in warnings:
            print(f"  - {w}")

    if failed:
        print()
        print(f"❌ 验证失败: {len(failed)} 项必须修复")
        sys.exit(1)
    else:
        print()
        print("✅ 全部错误级检查通过" + (f" (含 {len(warnings)} 项警告)" if warnings else ""))
        sys.exit(0)


if __name__ == "__main__":
    main()
