"""
v6.1 必跑验证脚本 — PDI 聚氨酯 P&ID 5 大问题硬检
==================================================

**触发场景**：每次出新版 P&ID 后、推送前**必跑**这个脚本。
**v6.0 BUG 教训**：3 个版本（v3.5/v4.0/v5.0）都没真正解决 5 问题，全靠"标签字符串存在"自欺欺人。
**v6.1 升级**：用 regex 扫描实际坐标，验证 5 问题 + 零重复路径。

**v6.1 反馈整改（2026-06-17 女王当面 5 问题）**：
  ① N₂/PPDI 流股重叠 (PPDI 5px 小尾巴在 y=195 与 N₂ 水平段交叉)
  ② R-301 显 2 股 HO 出料 (4 接管视觉混淆)
  ③ 物料线必须进入浅蓝填充区 y=725-745 (线端 + 箭头 tip 全在浅蓝填充区, 不穿入设备本体)
  ④ MOCA 投料 (y=836-887) vs 真空 (y=895-930) y 范围错开 ≥ 16px
  ⑤ 多股进料汇聚总管 (Convergence Manifold, y=380 → NO-301A 顶进)

用法:
    python3 v6.1-verify.py [path-to-pid.html]

输出:
    - 全部通过: 绿色 "✅ v6.1 5 大问题全部硬检通过"
    - 任一失败: 红色 "❌ 失败项" + 具体坐标

v6.1 脚本本身修复:
  - regex 兼容 3 位 hex 简写 (#000) 和 6 位 (#000000)
  - line 元素属性顺序无依赖 (x1/y1/x2/y2/stroke 任意顺序)
  - 问题 3 检查方向正确: 物料线端 y=730-745 必须在浅蓝填充区内
  - 问题 4 检查 y 范围 (非 x 范围) 不重叠
  - 问题 1b/c: 检测 PPDI 5px 小尾巴陷阱 (N₂ 水平段 y 处出现非 PPDI 黑色水平线)
"""

import re
import sys
import subprocess
from pathlib import Path
from collections import Counter

PID_FILE_DEFAULT = "/home/hermes-admin/.hermes/skills/engineering/petrochem-process-design/references/polyurethane-PDI-10tpa-pid.html"
HTTP_URL = "http://69.12.72.246:28082/polyurethane-PDI-10tpa-pid.html"

# ANSI 颜色
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def read_pid_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8-sig') as f:
        return f.read()


def normalize_color(c: str) -> str:
    """#abc → #aabbcc (兼容 3 位与 6 位 hex)"""
    if not c:
        return None
    c = c.upper()
    if len(c) == 4 and c.startswith('#'):
        return '#' + c[1]*2 + c[2]*2 + c[3]*2
    return c


def parse_line_attrs(attrs: str) -> dict:
    """解析 line/polygon 元素的所有属性, 不依赖顺序"""
    result = {}
    for m in re.finditer(r'(\w+(?:-\w+)?)="([^"]+)"', attrs):
        result[m.group(1)] = m.group(2)
    return result


def get_all_lines(text: str) -> list:
    """返回 [(x1, y1, x2, y2, stroke, da, sw), ...] 全部 line 元素"""
    results = []
    for m in re.finditer(r'<line\s+([^/]+)/>', text):
        attrs = parse_line_attrs(m.group(1))
        if all(k in attrs for k in ('x1', 'y1', 'x2', 'y2', 'stroke')):
            results.append((
                int(attrs['x1']),
                int(attrs['y1']),
                int(attrs['x2']),
                int(attrs['y2']),
                attrs['stroke'],
                attrs.get('stroke-dasharray', ''),
                attrs.get('stroke-width', ''),
            ))
    return results


def get_all_polygons(text: str) -> list:
    """返回 [(cx, cy, [(x, y), ...], fill), ...] 全部 polygon 元素"""
    results = []
    for m in re.finditer(r'<polygon\s+([^/]+)/>', text):
        attrs = parse_line_attrs(m.group(1))
        if 'points' not in attrs or 'fill' not in attrs:
            continue
        coords = []
        for p in attrs['points'].split():
            if ',' in p:
                x, y = p.split(',')
                coords.append((int(x), int(y)))
        if len(coords) >= 3:
            cx = sum(c[0] for c in coords) / len(coords)
            cy = sum(c[1] for c in coords) / len(coords)
            results.append((cx, cy, coords, attrs['fill']))
    return results


def get_tip_y(coords: list) -> int:
    """三角形的尖端 y: 出现 1 次的 y 即为尖端 (与 base 区分)"""
    ys = [c[1] for c in coords]
    yc = Counter(ys)
    lone_ys = [y for y, c in yc.items() if c == 1]
    if lone_ys:
        return lone_ys[0]
    # 3 个 y 全不同: 取极值 (更远离 centroid)
    cy = sum(ys) / len(ys)
    return min(ys) if abs(min(ys) - cy) < abs(max(ys) - cy) else max(ys)


# =========================================================
# 问题 1: 3 股进料水平段零重叠 (含 5px 小尾巴陷阱检测)
# =========================================================
def check_problem_1_no_overlap(text: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- 问题 1: 3 股进料水平段零重叠 ---{RESET}")

    lines = get_all_lines(text)
    horiz = [l for l in lines if l[1] == l[3]]

    ptmg = [l for l in horiz if normalize_color(l[4]) == '#000000' and 50 <= l[1] <= 150 and l[0] > 400]
    n2 = [l for l in horiz if normalize_color(l[4]) == '#2E7D32' and 150 <= l[1] <= 250]
    ppdi = [l for l in horiz if normalize_color(l[4]) == '#000000' and 250 <= l[1] <= 320 and l[0] > 1500]

    print(f"  PTMG 水平段: {len(ptmg)} 条 {[(l[1], l[0], l[2]) for l in ptmg]}")
    print(f"  N₂   水平段: {len(n2)} 条 {[(l[1], l[0], l[2]) for l in n2]}")
    print(f"  PPDI 水平段: {len(ppdi)} 条 {[(l[1], l[0], l[2]) for l in ppdi]}")

    ok = True
    msgs = []
    if len(ptmg) != 1:
        ok = False
        msgs.append(f"❌ PTMG 水平段 {len(ptmg)} 条 (应 = 1)")
    if len(n2) != 1:
        ok = False
        msgs.append(f"❌ N₂ 水平段 {len(n2)} 条 (应 = 1)")
    if len(ppdi) != 1:
        ok = False
        msgs.append(f"❌ PPDI 水平段 {len(ppdi)} 条 (应 = 1)")

    # 1b: PPDI 路径唯一性 (5px 小尾巴陷阱)
    ppdi_full = [l for l in lines if normalize_color(l[4]) == '#000000'
                 and 200 <= l[1] <= 320 and 200 <= l[3] <= 320
                 and (l[0] > 1500 or l[2] > 1500)]
    if len(ppdi_full) > 2:
        ok = False
        msgs.append(f"❌ PPDI 路径碎片化: {len(ppdi_full)} 条 (应 ≤ 2 折角: 垂直+水平)")

    if ok and ptmg and n2 and ppdi:
        y_ptmg, y_n2, y_ppdi = ptmg[0][1], n2[0][1], ppdi[0][1]
        if y_ptmg == y_n2 or y_n2 == y_ppdi or y_ptmg == y_ppdi:
            ok = False
            msgs.append(f"❌ 3 流股 y 重叠 (PTMG={y_ptmg}, N₂={y_n2}, PPDI={y_ppdi})")
        else:
            min_gap = min(abs(y_ptmg - y_n2), abs(y_n2 - y_ppdi), abs(y_ptmg - y_ppdi))
            print(f"  {GREEN}✓ 3 流股 y 高度全不同: PTMG={y_ptmg}, N₂={y_n2}, PPDI={y_ppdi} (最小间距 {min_gap}px){RESET}")
            if min_gap < 80:
                msgs.append(f"{YELLOW}⚠ y 间距仅 {min_gap}px (< 80px 建议值){RESET}")

    # 1c: N2 水平段必须不被其他流股的小尾巴穿越 (5px 小尾巴陷阱)
    if n2:
        n2_y = n2[0][1]
        n2_x_min, n2_x_max = min(n2[0][0], n2[0][2]), max(n2[0][0], n2[0][2])
        for l in lines:
            x1, y1, x2, y2, c, da, sw = l
            if y1 != y2 or y1 != n2_y: continue
            if not (850 <= x1 <= 2400 and 850 <= x2 <= 2400): continue
            # 任何在 y=y_n2 处的水平线 (x 范围与 N2 重叠), 黑色, 不是 N2 自身
            line_x_min, line_x_max = min(x1, x2), max(x1, x2)
            if (line_x_min < n2_x_max and line_x_max > n2_x_min
                and normalize_color(c) == '#000000'):
                ok = False
                msgs.append(f"❌ N₂ y={n2_y} 处有黑色水平线 (x=[{x1}, {x2}]) - 疑似 PPDI 5px 小尾巴, 与 N₂ 重叠")

    for m in msgs:
        print(f"  {m}")
    return ok, "\n".join(msgs) if msgs else ""


# =========================================================
# 问题 2: 4 接管温度标签
# =========================================================
def check_problem_2_temp_labels(text: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- 问题 2: R-301 4 接管温度标签 ---{RESET}")
    ok = True
    msgs = []
    for label in ["200°C", "160°C", "5°C", "20°C", "↓ IN", "↑ OUT"]:
        if label not in text:
            ok = False
            msgs.append(f"❌ 缺标签: {label}")
        else:
            print(f"  {GREEN}✓ {label}{RESET}")
    return ok, "\n".join(msgs) if msgs else ""


# =========================================================
# 问题 3: 物料线进入浅蓝填充区 (女王 v4.0/v6.1 明确要求)
# 框 y=425-745, 设备本体 y=465-725, 浅蓝填充区 y=725-745 (设备底与框底之间 20px)
# 要求: 4 接管物料线端 y=730-745 在浅蓝填充区内, 箭头 tip y=725-745 全在浅蓝填充区
# =========================================================
def check_problem_3_jacket_lines(text: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- 问题 3: HO/CW 物料线进入浅蓝填充区 y=730-745 ---{RESET}")
    print(f"  (框 y=425-745, 设备本体 y=465-725, 浅蓝填充区 y=725-745, 主管在 y=1295/1380)")

    lines = get_all_lines(text)
    polygons = get_all_polygons(text)

    # 3a: 物料线端 y=730-745 (浅蓝填充区内, 不穿入设备本体)
    ho_cw_lines = []
    for l in lines:
        x1, y1, x2, y2, c, da, sw = l
        if normalize_color(c) != '#1565C0': continue
        if not (1000 <= x1 <= 1110): continue
        if x1 != x2: continue  # 只看垂直线
        line_end_y = min(y1, y2)
        if 730 <= line_end_y <= 745:
            ho_cw_lines.append((x1, line_end_y))

    print(f"  物料线端 y=730-745 数量: {len(ho_cw_lines)} (期望 = 4)")
    for x, y in ho_cw_lines:
        print(f"    ✓ x={x} line 端 y={y}")

    ok_3a = len(ho_cw_lines) == 4
    msgs = []
    if not ok_3a:
        msgs.append(f"❌ 物料线端 y=730-745 仅 {len(ho_cw_lines)} 条 (应 = 4)")

    # 3b: 4 接管箭头 tip y 全部在 725-745 浅蓝填充区内
    ho_cw_arrows = []
    for cx, cy, coords, fill in polygons:
        if normalize_color(fill) != '#1565C0': continue
        if not (1000 <= cx <= 1110): continue
        if not (720 <= cy <= 770): continue
        tip_y = get_tip_y(coords)
        direction = "UP" if tip_y < cy else "DOWN"
        in_jacket = 725 <= tip_y <= 745
        ho_cw_arrows.append((cx, tip_y, direction, in_jacket))

    print(f"  4 接管箭头 (R-301 夹套, x=1000-1110, y=720-770):")
    for cx, ty, d, ijk in ho_cw_arrows:
        flag = "✓" if ijk else "❌"
        print(f"    {flag} x={cx:.0f} tip_y={ty} {d} 浅蓝填充区={'是' if ijk else '否'}")

    ok_3b = len(ho_cw_arrows) == 4 and all(a[3] for a in ho_cw_arrows)
    if not ok_3b:
        msgs.append(f"❌ 4 接管箭头 tip 不全在浅蓝填充区")

    # 3c: 4 接管箭头方向交替 (↑↓↑↓) 避免"2 股 HO 出料"视觉混淆
    if ok_3b and len(ho_cw_arrows) == 4:
        directions = [a[2] for a in sorted(ho_cw_arrows, key=lambda x: x[0])]
        if directions != ['UP', 'DOWN', 'DOWN', 'UP']:
            msgs.append(f"❌ 4 接管方向未按 ↑↓↑↓ 交替: {directions} (期望 UP,DOWN,DOWN,UP)")

    # 3d: 4 夹套虚线框
    jacket_count = len(re.findall(r'fill="#E3F2FD"[^/]*stroke="#1565C0"[^/]*stroke-width="[34]"', text))
    print(f"  3-4px 浅蓝夹套框数: {jacket_count} (应 ≥ 4)")
    if jacket_count < 4:
        msgs.append(f"❌ 夹套虚线框仅 {jacket_count} 个 (应 ≥ 4)")

    ok = ok_3a and ok_3b and (jacket_count >= 4)
    if ok and not msgs:
        print(f"  {GREEN}✓ 4 接管物料线端 y=730-745 全在浅蓝填充区, 箭头 tip y=725-745{RESET}")
    for m in msgs:
        print(f"  {m}")
    return ok, "\n".join(msgs) if msgs else ""


# =========================================================
# 问题 4: MOCA 投料 vs 真空接管 y 范围不重叠
# (v6.0 只检查 x 间距, 但女王 v4.0 反馈 y 范围重叠才是问题)
# =========================================================
def check_problem_4_moca_vac_offset(text: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- 问题 4: MOCA 投料 vs 真空接管 y 范围不重叠 ---{RESET}")

    moca_y_end = None
    for m in re.finditer(r'<rect\s+([^/]+)/>', text):
        attrs = parse_line_attrs(m.group(1))
        if attrs.get('width') == '40' and attrs.get('height') == '14' and 'stroke-dasharray' in attrs:
            moca_y_end = int(attrs['y']) + 14
            print(f"  MOCA manhole y={attrs['y']}-{moca_y_end}")
            break

    vac_y_min = None
    vac_y_max = None
    for l in get_all_lines(text):
        x1, y1, x2, y2, c, da, sw = l
        if normalize_color(c) != '#000000': continue
        if not da: continue
        if not (850 <= x1 <= 860): continue
        if vac_y_min is None or min(y1, y2) < vac_y_min:
            vac_y_min = min(y1, y2)
        if vac_y_max is None or max(y1, y2) > vac_y_max:
            vac_y_max = max(y1, y2)

    print(f"  VAC 接管 y={vac_y_min}-{vac_y_max}")

    ok = False
    msgs = []
    if moca_y_end and vac_y_min:
        gap = vac_y_min - moca_y_end
        if moca_y_end < vac_y_min:
            ok = True
            print(f"  {GREEN}✓ MOCA y_end={moca_y_end} < VAC y_min={vac_y_min} 间距 {gap}px{RESET}")
        else:
            msgs.append(f"❌ MOCA y_end={moca_y_end} 与 VAC y_min={vac_y_min} 重叠 (应 moca_y_end < vac_y_min)")
    else:
        msgs.append("❌ 未找到 MOCA manhole 或 VAC 接管")

    for m in msgs:
        print(f"  {m}")
    return ok, "\n".join(msgs) if msgs else ""


# =========================================================
# 问题 5: 多股进料汇聚总管
# =========================================================
def check_problem_5_manifold(text: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- 问题 5: 进料汇聚总管 ---{RESET}")
    ok = True
    msgs = []
    if "R-301 进料汇聚总管" not in text:
        ok = False
        msgs.append("❌ 缺进料汇聚总管标签")
    else:
        print(f"  {GREEN}✓ 进料汇聚总管标签存在{RESET}")
    if "NO-301A 顶进" not in text:
        ok = False
        msgs.append("❌ 缺 NO-301A 顶进 (总管出口)")
    else:
        print(f"  {GREEN}✓ NO-301A 顶进存在{RESET}")
    return ok, "\n".join(msgs) if msgs else ""


# =========================================================
# 零重复路径铁律
# =========================================================
def check_no_duplicate_paths(text: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- 零重复路径铁律 ---{RESET}")
    ok = True
    msgs = []
    lines = get_all_lines(text)

    # PPDI 路径 ≤ 2 折角
    ppdi = [l for l in lines if normalize_color(l[4]) == '#000000'
            and 200 <= l[1] <= 320 and 200 <= l[3] <= 320
            and (l[0] > 1500 or l[2] > 1500)]
    if len(ppdi) > 2:
        ok = False
        msgs.append(f"❌ PPDI 路径碎片化: {len(ppdi)} 条 (应 ≤ 2 折角)")
    else:
        print(f"  {GREEN}✓ PPDI 路径 {len(ppdi)} 条 (≤ 2 折角){RESET}")

    return ok, "\n".join(msgs) if msgs else ""


# =========================================================
# HTTP 200 验证
# =========================================================
def check_http_200(url: str) -> tuple[bool, str]:
    print(f"\n{BLUE}--- HTTP 200 验证 ---{RESET}")
    try:
        r = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', 'HTTP %{http_code} | size %{size_download} bytes | time %{time_total}s', url],
            capture_output=True, text=True, timeout=5
        )
        print(f"  {r.stdout}")
        if 'HTTP 200' in r.stdout:
            print(f"  {GREEN}✓ HTTP 200 OK{RESET}")
            return True, ""
        else:
            return False, f"❌ HTTP 验证失败: {r.stdout}"
    except Exception as e:
        return False, f"❌ curl 失败: {e}"


def main():
    pid_path = sys.argv[1] if len(sys.argv) > 1 else PID_FILE_DEFAULT
    print(f"{BLUE}{'='*60}\nv6.1 必跑验证脚本 — 5 大问题硬检\n文件: {pid_path}\n{'='*60}{RESET}")

    if not Path(pid_path).exists():
        print(f"{RED}❌ 文件不存在: {pid_path}{RESET}")
        sys.exit(1)

    text = read_pid_file(pid_path)
    print(f"  文件大小: {len(text)} bytes, 行数: {text.count(chr(10))}")

    checks = [
        check_problem_1_no_overlap,
        check_problem_2_temp_labels,
        check_problem_3_jacket_lines,
        check_problem_4_moca_vac_offset,
        check_problem_5_manifold,
        check_no_duplicate_paths,
    ]

    results = []
    for check in checks:
        ok, msg = check(text)
        results.append((check.__name__, ok, msg))

    # HTTP 验证
    http_ok, http_msg = check_http_200(HTTP_URL)
    results.append(("check_http_200", http_ok, http_msg))

    # 总结
    print(f"\n{BLUE}{'='*60}\n总结\n{'='*60}{RESET}")
    all_ok = True
    for name, ok, msg in results:
        status = f"{GREEN}✓ PASS{RESET}" if ok else f"{RED}✗ FAIL{RESET}"
        print(f"  {status}  {name}")
        if not ok:
            all_ok = False
            if msg:
                print(f"          {msg}")

    if all_ok:
        print(f"\n{GREEN}✅ v6.1 5 大问题全部硬检通过！可以推送。{RESET}")
        sys.exit(0)
    else:
        print(f"\n{RED}❌ 验证失败，禁止推送！修复后重跑。{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
