# CoolProp 物性库 — 安装与使用模板

> **首次落地**: 2026-06-30 / Sir 安装 + 4 demo 跑通 / 女王 06-30 WeChat 已汇报

## 1. 安装位置

- **Python venv**: `/home/hermes-admin/venv`（Sir 现有 venv, 已用 uv 装入）
- **包**: `coolprop==8.0.0` + `numpy==2.5.0`
- **安装命令**: `uv pip install --python /home/hermes-admin/venv/bin/python CoolProp`

## 2. Demo 脚本

`scripts/coolprop_demo.py` —— 4 个 demo:
1. N₂ 减压阀流量核算 (PCV-101B 第二级)
2. 甲苯储罐 PSV 整定压力 (V-101/102/103)
3. V-401 真空蒸馏 10 mbar 沸点 (v6.9 真空度)
4. 女王常用 20 种组分速查 (T_c / P_c / M / ρ_liq)

调用:
```bash
/home/hermes-admin/venv/bin/python ~/.hermes/skills/engineering/petrochem-process-design/scripts/coolprop_demo.py
```

## 3. 标准 API 范式 (PropsSI)

```python
import CoolProp.CoolProp as CP

# 单点物性
P_sat = CP.PropsSI('P', 'T', 363.15, 'Q', 0, 'Water')          # 90℃ 水饱和蒸汽压
rho   = CP.PropsSI('D', 'P', 90000, 'T', 303.15, 'n-Hexane')   # 90 kPa / 30℃ 己烷密度
cp    = CP.PropsSI('d(Hmass)/d(T)|P', 'P', 101325, 'T', 350, 'Water')  # 水的 cp

# 临界参数
T_c = CP.PropsSI('Tcrit', 'Water')   # K
P_c = CP.PropsSI('Pcrit', 'Water')   # Pa
M   = CP.PropsSI('M', 'Water')       # kg/mol

# 自定义混合物
mix = CP.PropsSI('D', 'T', 350, 'P', 101325, 'n-Hexane[0.5]&Toluene[0.5]')

# 相态查询
phase = CP.PhaseSI('P', 101325, 'T', 350, 'Water')
```

## 4. 适配场景 (女王工作)

| 工作 | CoolProp 适配 | 备注 |
|------|--------------|------|
| N₂ 减压阀流量 | ✅ | N₂ / Air 全覆盖 |
| 储罐 PSV 整定 | ✅ | Toluene / Water / n-Hexane 全覆盖 |
| 真空蒸馏 10 mbar | ✅ (单组分) | 多元需 mixing rules + 进料组成 |
| P&ID v6.9 出图 | ❌ | 纯绘图规则, 物性查询可辅助但非主用途 |
| TDI 核心反应 | ❌ | CoolProp 无 TDI/TDA/Phosgene, 需自定义 EOS |
| 硝化反应 | ❌ | 强酸体系 CoolProp 弱 |

## 5. 女王常用组分对照 (节选, 全 136 种)

| 工艺名 | CoolProp 名 | 类别 |
|--------|------------|------|
| 水 | `Water` | 通用 |
| 氮气 | `Nitrogen` | 公用工程 |
| 氧气 | `Oxygen` | 公用工程 |
| 空气 | `Air` | 公用工程 |
| 氨 | `Ammonia` | 反应物 |
| 氯化氢 | `HydrogenChloride` | 反应物 |
| 硫化氢 | `HydrogenSulfide` | 反应物 |
| CO2 | `CarbonDioxide` | 副产/排放 |
| CO | `CarbonMonoxide` | 反应物 |
| 甲烷 | `Methane` | 轻烃 |
| 乙烷 | `Ethane` | 轻烃 |
| 丙烷 | `n-Propane` | 轻烃 |
| 丁烷 | `n-Butane` | 轻烃 |
| 戊烷 | `n-Pentane` | 轻烃 |
| 己烷 | `n-Hexane` | 轻烃 (仁信 90 kPa 储罐介质) |
| 甲苯 | `Toluene` | TDI 原料 |
| 苯 | `Benzene` | 溶剂 |
| 甲醇 | `Methanol` | 溶剂 |
| 乙醇 | `Ethanol` | 溶剂 |
| 丙酮 | `Acetone` | 溶剂 |

## 6. 缺失组分 (需自定义或代理)

- **TDI** (甲苯二异氰酸酯 C9H6N2O2): CoolProp 无, 代理用 Toluene + 经验修正
- **TDA** (甲苯二胺 C7H10N2): 无, 代理同上
- **光气** (COCl2): 无, 剧毒, CoolProp 不收录
- **ODB** (邻二氯苯 C6H4Cl2): 无, 代理可用 o-Xylene
- **氯苯** (C6H5Cl): 无, 代理可用 Benzene
- **甲醛** (CH2O): 无, 代理用 Methanol
- **苯胺** (C6H7N): 无, 代理用 Toluene
- **MDI** (C15H10N2O2): 无, 代理困难

**自定义 Helmholtz EOS 路径** (前置条件):
- 蒸气压曲线多点
- 饱和液相/气相密度
- 理想气体比热 cp0
- 黏度 / 导热系数
- 表面张力
- 熔化曲线

无上述实验物性数据时, 走"代理估算"路径, 不强行自定义。

## 7. 已知坑 (2026-06-30 跑通时发现)

1. **`PropsSI('D','P',P,'T',T,fluid)` 在饱和点会报错** ("bad input for other")
   - 原因: 饱和点 (P,T,Q=0/1) 三个状态变量中, 给两个就够, 给三个过约束
   - 解决: 饱和点查询用 `(P, Q=1)` 或 `(T, Q=1)`, 不要再补 T 或 P

2. **`PropsSI('D','T',293.15,'Q',0,fluid)` 在 T > T_crit 时报错**
   - 原因: 临界点之上没有"饱和液"概念
   - 解决: 先查 T_crit, 低于 T_crit 用 `Q=0` 取饱和液, 高于 T_crit 用 `(T, P=101325)` 取气态

3. **缺失流体抛异常**: 不要 `try/except` 静默吞, 必须显式报"流体不在 CoolProp 库, 需自定义或代理"

4. **大量调用慢**: 460+ 次 PropsSI 需 5-10 秒, 高频场景考虑 SQLite 缓存 (本次未启用, 待工艺计算实际触发时再装)

## 8. 触发 CoolProp 的判据

**该用 CoolProp 时**:
- 工艺计算书需要 T_c / P_c / M / cp / ρ / μ / λ / σ
- 储罐 PSV 整定需要饱和蒸汽压
- 真空泵选型需要绝压沸点
- 减压阀流量需要密度
- 混合物平衡 (Helmholtz + mixing rules)

**不该用 CoolProp 时**:
- 简单理想气体计算 (PV=nRT 即可)
- 标准手册已给数据的常规物性 (查 SH/T 3045 / API 521)
- 非稳态、非平衡态 (如反应动力学)
- 真实多组分相平衡需活度系数模型 (NRTL / UNIQUAC, 而非 Helmholtz)

## 9. 后续任务挂钩

按 Sir 增量式指示 (06-30), 以下功能**留到工艺计算实际触发再装**:
- SQLite 缓存层 (高频查询提速 10×)
- 女王常用流体 CoolProp 名对照完整版
- 多元混合物 mixing rules 模板 (VLE / 精馏)
- 自定义 Helmholtz EOS 框架 (TDI/TDA 走不通时用)

## 10. 相关文件

- `scripts/coolprop_demo.py` — 4 个 demo 跑通脚本
- `~/.hermes/skills/engineering/pressure-vessel-expert/scripts/process_pdf_batch.py` — PDF OCR 脚本 (2026-06-30 已 patch OOM bug, 见 `references/knowledge-base-recovery.md` §8)
- CoolProp 官方文档: http://www.coolprop.org/