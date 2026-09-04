# Windows 11 兼容 HTML 骨架模板（PFD / P&ID 通用）

> **本模板是 2026-06-06 女王当面纠正"PDI P&ID 打不开"事件后固化的合规模板**。
> 复制本骨架 → 替换设备/物流/仪表内容 → 自动满足 Windows 11 / Edge / Chrome / Firefox / IE 11 基础显示。

---

## 完整骨架（直接复制）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>项目 P&ID/PFD — Windows 11 兼容版</title>
</head>
<body style="font-family:'Microsoft YaHei','SimHei','SimSun',Arial,sans-serif;font-size:12px;margin:8px;">

<!-- ========== 标题栏 ========== -->
<table border="0" cellpadding="6" cellspacing="0" width="100%" style="background:#0d47a1;color:#ffffff;border:2px solid #000000;">
<tr><td style="background:#0d47a1;color:#ffffff;">
  <b style="font-size:18px;">项目名称 — 工艺流程图 P&ID</b><br>
  <span style="font-size:12px;">覆盖单元：100 原料储存 + 200 ... + 700 公共工程</span><br>
  <span style="font-size:11px;">工艺：xxx 体系 | 规模：xx t/a | 设计阶段：xxx | 版本 v1.0 Windows 11 兼容版 | 日期</span>
</td></tr>
</table>

<!-- ========== 图例 ========== -->
<table border="1" cellpadding="4" cellspacing="0" width="100%" style="background:#fafafa;font-size:11px;">
<tr style="background:#bbdefb;">
<th colspan="8">图例与符号说明</th>
</tr>
<tr style="background:#ffffff;">
<td><b>线型：</b></td>
<td><hr style="border:0;border-top:2px solid #000;width:50px;display:inline-block;margin:0;"> 主工艺物流</td>
<td><hr style="border:0;border-top:2px dashed #1565c0;width:50px;display:inline-block;margin:0;"> 公用工程</td>
<td><hr style="border:0;border-top:2px dashed #2e7d32;width:50px;display:inline-block;margin:0;"> N₂ / 真空</td>
<td colspan="4"></td>
</tr>
<tr style="background:#ffffff;">
<td><b>阀门：</b></td>
<td>▌▌ 闸阀 Z (Z41H-16C)</td>
<td>◀▶ 球阀 Q (Q41F-16C)</td>
<td>⊥ 截止阀 J (J41H-16C)</td>
<td>▷◁ 止回阀 H (H44H-16C)</td>
<td>Ⓢ 安全阀 (A42Y-16C)</td>
<td>Ⓡ 爆破片 (YP)</td>
<td>Ⓒ 调节阀 (ZJHP-16K)</td>
</tr>
<tr style="background:#ffffff;">
<td><b>仪表：</b></td>
<td>○PI 压力显示</td>
<td>○TI 温度显示</td>
<td>○LI 液位显示</td>
<td>○FI 流量显示</td>
<td>○QI 转速显示</td>
<td>○AT 分析</td>
<td>◎TIRC 记录控制</td>
</tr>
</table>

<!-- ========== 单元 100 ========== -->
<br>
<table border="0" cellpadding="4" cellspacing="0" width="100%">
<tr><td style="background:#0d47a1;color:#ffffff;font-size:14px;font-weight:bold;padding:6px;border:2px solid #000000;">
100 单元 — 单元名称
</td></tr>
</table>

<table border="1" cellpadding="4" cellspacing="0" width="100%">
<tr style="background:#bbdefb;">
<th>设备位号</th><th>名称</th><th>规格</th><th>材质</th><th>主要接管</th><th>仪表</th><th>阀门</th>
</tr>
<tr>
<td style="background:#fffacd;text-align:center;font-weight:bold;color:#c62828;">V-101</td>
<td>xxx 储罐</td>
<td>xxx L 立式</td>
<td>304SS</td>
<td>
N1 进料 DN50<br>
N2 出料 DN50<br>
N3 N₂ 封 DN25
</td>
<td>LI-101（磁翻板+远传）<br>TI-101（Pt100）<br>PI-101（压力表）</td>
<td>V-101A Z41H-16C DN50 进料<br>V-101B Z41H-16C DN50 出料<br>V-101C Q41F-16C DN25 N₂</td>
</tr>
</table>

<!-- ========== 单元 200 / 300 ... 重复上面结构 ========== -->

<!-- ========== SIS 联锁总览 ========== -->
<br>
<table border="0" cellpadding="4" cellspacing="0" width="100%">
<tr><td style="background:#c62828;color:#ffffff;font-size:14px;font-weight:bold;padding:6px;border:2px solid #000000;">
🛡️ SIS 安全仪表系统（联锁逻辑总览）
</td></tr>
</table>

<table border="1" cellpadding="4" cellspacing="0" width="100%">
<tr style="background:#bbdefb;">
<th>SIS 位号</th><th>触发条件</th><th>动作 1</th><th>动作 2</th><th>动作 3</th><th>动作 4</th><th>SIL 等级</th>
</tr>
<tr><td>SIS-301A</td><td>R-301 温度 T&gt;95°C（高高）</td><td>切断 PPDI 进料</td><td>启动冷冻水最大</td><td>关导热油</td><td>声光报警</td><td><b style="color:#c62828;">SIL 2</b></td></tr>
</table>

<!-- ========== 阀门汇总表 ========== -->
<br>
<table border="0" cellpadding="4" cellspacing="0" width="100%">
<tr><td style="background:#0d47a1;color:#ffffff;font-size:14px;font-weight:bold;padding:6px;border:2px solid #000000;">
阀门类型与规格汇总表
</td></tr>
</table>

<table border="1" cellpadding="4" cellspacing="0" width="100%">
<tr style="background:#bbdefb;">
<th>代号</th><th>阀门类型</th><th>型号</th><th>DN</th><th>PN</th><th>材质</th><th>数量</th><th>用途</th>
</tr>
<tr><td>▌Z 闸阀</td><td>闸阀</td><td>Z41H-16C</td><td>DN15~DN80</td><td>PN16</td><td>WCB+304SS</td><td>~50</td><td>通用切断</td></tr>
</table>

<!-- ========== 现场仪表清单 ========== -->
<br>
<table border="0" cellpadding="4" cellspacing="0" width="100%">
<tr><td style="background:#0d47a1;color:#ffffff;font-size:14px;font-weight:bold;padding:6px;border:2px solid #000000;">
现场仪表清单
</td></tr>
</table>

<table border="1" cellpadding="4" cellspacing="0" width="100%">
<tr style="background:#bbdefb;">
<th>位号</th><th>测量变量</th><th>仪表类型</th><th>量程</th><th>安装位置</th><th>信号</th><th>防爆</th>
</tr>
<tr><td>TI-301</td><td>温度</td><td>Pt100 热电阻</td><td>0~200°C</td><td>R-301 顶部</td><td>4-20 mA + HART</td><td>Exd IIB T4</td></tr>
</table>

<!-- ========== 关键提示 ========== -->
<br>
<table border="0" cellpadding="4" cellspacing="0" width="100%" style="background:#ffebee;border:3px solid #c62828;">
<tr><td style="background:#ffebee;padding:8px;">
<b style="color:#c62828;">⚠ 关键提示：</b>
<ol>
<li>提示 1</li>
<li>提示 2</li>
</ol>
</td></tr>
</table>

<br>
<table border="0" cellpadding="4" cellspacing="0" width="100%" style="background:#e8f5e9;border:3px solid #2e7d32;">
<tr><td style="background:#e8f5e9;padding:8px;">
<b style="color:#2e7d32;">✓ 完整度自检：</b>
<ul>
<li>✅ 检查项 1</li>
<li>✅ 检查项 2</li>
</ul>
</td></tr>
</table>

<p style="font-size:10px;color:#666;margin-top:8px;text-align:center;">
文档版本：v1.0 Windows 11 兼容版 | 日期<br>
兼容性测试：Microsoft Edge 99+、Chrome 90+、Firefox 88+、IE 11（基础显示）
</p>

</body>
</html>
```

---

## 保存后必做的两步

### 1. 加 UTF-8 BOM（Windows 记事本友好）

```python
# Python 3 脚本
path = "your-pid.html"
with open(path, 'rb') as f:
    content = f.read()
if not content.startswith(b'\xef\xbb\xbf'):
    with open(path, 'wb') as f:
        f.write(b'\xef\xbb\xbf' + content)
print("已加 UTF-8 BOM")
```

### 2. 验证文件

```bash
file your-pid.html
# 期望输出：HTML document, Unicode text, UTF-8 (with BOM) text
```

---

## 复用的关键约束（再次提醒）

| 项 | 要求 | 后果（违反时）|
|----|------|--------------|
| **零现代 CSS** | 无 flex/grid/clip-path/伪元素/border-radius 圆形 | Edge 旧版/IE 不渲染 |
| **纯内联样式** | 每个标签 `style="..."` | 部分 IE 屏蔽 `<style>` 块 |
| **UTF-8 BOM** | 文件首三字节 `\xef\xbb\xbf` | 记事本中文乱码 |
| **必备 meta** | `<meta charset="UTF-8">` + `<meta X-UA-Compatible>` | 编码错 / IE 降级 |
| **多级字体回退** | 'Microsoft YaHei','SimHei','SimSun',Arial,sans-serif | 部分 Win11 缺字体 |
| **Unicode 阀门符号** | ▌◀⊥▷◁ⓈⓇⒸ | 无 CSS 图形可显示 |
| **表格布局** | 全部 `<table>` | flex/grid 在 IE 11 异常 |
| **< 100 KB** | 单元数 ≤ 8 | 微信/企业邮箱附件上限 |

---

## 实战案例（已验证可用）

- `references/polyurethane-PDI-10tpa-pfd.html` — 22.5 KB，100~700 全覆盖
- `references/polyurethane-PDI-10tpa-pid.html` — 40.2 KB，100~700 全覆盖

均经 2026-06-06 女王微信实测可正常打开。

---

## 修改建议

- 改设备数量：复制 `<tr>...</tr>` 行，按需增加
- 改颜色：搜索 `#0d47a1`（标题蓝）/ `#c62828`（核心红）/ `#2e7d32`（安全绿）三色，全局替换
- 改单元数：复制单元标题块（`<br><table>...</table>`）
- 改字体：批量替换 `Microsoft YaHei` 为项目字体（保留多级回退）

---

## 历史教训（2026-06-06 女王当面纠正）

> 上一版 P&ID（v1.0）用了 `clip-path: polygon()` / `display: flex` / `::after` 等 4 类现代 CSS 特性 + 未加 UTF-8 BOM，导致**整个 P&ID 在 Windows 11 Edge 打不开**。
> 
> 女王原话："MEDIA:/.../polyurethane-PDI-10tpa-pid.html 这个打不开，生成 Windows 11 网页版能打开的 .HTML 格式的"
> 
> 根因：默认浏览器安全策略 + IE 兼容回退失败 + 记事本编码识别失败
> 
> **修复：v2.0 重写后女王微信实测可用**。本模板是 v2.0 的骨架固化版。
