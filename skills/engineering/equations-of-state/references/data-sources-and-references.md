# EOS 数据源与查表路径 — NIST / REFPROP / CoolProp / JANAF / DIPPR 速查

> **本文件是 equations-of-state SKILL 的 references/ 详解之一**。
> 为女王工程查物性数据提供"按介质类型找数据源"的快速路径。

---

## 一、数据源总览

### 1.1 五大数据源(按权威性排序)

| 数据源 | 权威性 | 范围 | 访问方式 |
|--------|--------|------|----------|
| **NIST WebBook** | ★★★★★ | 流体物性(NIST 标准)| 免费 webbook.nist.gov |
| **NIST REFPROP** | ★★★★★ | NIST 流体库的高精度计算 | 商业 REFPROP 软件 |
| **CoolProp** | ★★★★☆ | 136 种流体,工程精度 | 开源 coolprop.org |
| **JANAF**(热化学表)| ★★★★★ | 化学反应热化学 | 商业 janaf.nist.gov |
| **DIPPR**(AIChE 物性数据库)| ★★★★☆ | 工业介质物性 | 商业 AIChE |

### 1.2 数据源快速对照

**女王工作流应该是:**
1. **常用物质(N₂, O₂, CO₂, CH₄, H₂O, 空气, 烃类)**:
   - 第一选择: **CoolProp 开源库** → 直接编程
   - 第二选择:**NIST WebBook** → 在线查
   - 校验:**NIST REFPROP** 或 **CoolProp + NIST 校核**

2. **新工艺新物质**:
   - 第一选择:**DIPPR DB**(商业)
   - 第二选择:**NIST WebBook**
   - 临时估算:**Reid 附录 A** + NIST TDE

3. **化学反应焓数据**:
   - 第一选择:**JANAF 热化学表**
   - 第二选择:**NIST WebBook + NIST TDE**

---

## 二、NIST WebBook

### 2.1 主页与查询入口

**网址:** https://webbook.nist.gov/chemistry/

**主要查询模块:**

| 模块 | 查询内容 | URL |
|------|----------|-----|
| **Fluid** | 流体物性(CO₂, H₂O, CH₄, ...)| webbook.nist.gov/chemistry/fluid/ |
| **Thermo** | 化学热力学 | webbook.nist.gov/chemistry/heat/ |
| **Reaction** | 反应平衡 + 焓 | webbook.nist.gov/chemistry/enthalpy/ |

### 2.2 NIST WebBook Fluid(女王最常用)

**查询物质:** NIST WebBook → Chemistry → Fluid

**输入方式:**
- 选物质:输入 CO₂ → 选 CO₂(Carbon dioxide)
- 输入 T, P(可查单点)
- 或选"Temperature & pressure sat**uration** properties"(饱和物性)

**CO₂ 输出示例(28°C, 8 MPa):**

```
Temperature:                          301.21 K(28.06 °C)
Pressure:                              8.00000 MPa
Density (state):                       764.91 kg/m³
Density (vapor):                       117.34 kg/m³
Speed of sound:                        322.34 m/s
Isobaric heat capacity, Cp:            4110 J/(kg·K)
Isochoric heat capacity, Cv:           740.0 J/(kg·K)
Internal energy, u:                    296.85 kJ/kg
Enthalpy, h:                           297.16 kJ/kg
Entropy, s:                            1.1247 kJ/(kg·K)
Helmholtz energy:                      h - T·s
```

### 2.3 NIST WebBook 适用范围

| 流体 | T 范围 | P 范围 | 来源 EOS |
|------|--------|--------|----------|
| **CO₂** | 216~1100 K | 0~800 MPa | Span-Wagner 1996 |
| **H₂O** | 273~2000 K | 0~1000 MPa | IAPWS-IF97 |
| **N₂** | 63~1000 K | 0~1000 MPa | Span-Wagner 2000 |
| **CH₄** | 90~625 K | 0~1000 MPa | Setzmann-Wagner |
| **Air** | 60~1000 K | 0~500 MPa | Lemmon |

### 2.4 女王工程中最常用的几个查询

**例 ①:CO₂ 在临界点附近的 ρ**
- 进入 webbook.nist.gov/chemistry/fluid/
- 输入 CO₂
- 设 T=304.25 K(临界温度), P=7.38 MPa(临界压力)
- 查得 ρ_c=467 kg/m³
- 任何"SCF 在临界附近"的设计都基于这一密度

**例 ②:CO₂ 在减压脱气阀出口的物性**
- 设定 T2 = 70°C, P = 4 MPa
- 查得 ρ ≈ 165 kg/m³, h ≈ +430 kJ/kg
- 与 EOS 计算一致

**例 ③:水的蒸汽压温度表**
- 设 P, 查 T_sat
- 设 T, 查 P_sat

---

## 三、NIST REFPROP

### 3.1 主程序特性

**REFPROP(NIST Reference Fluid Thermodynamic and Transport Properties Database)**

**版本:** REFPROP 10.0
**开发者:** NIST
**类型:** 商业软件(官方)

**价格:** 个人版数百美元,工坊组织版 ~数千美元/年

**包含流体数:** ~150 种高纯度流体 + ~5000 种混合物的混合规则
**所有流体都基于精确 EOS(Span-Wagner 系列)**

### 3.2 REFPROP 关键特性

| 项 | REFPROP |
|----|---------|
| **CO₂ EOS** | Span-Wagner 1996(精度最高)|
| **蒸汽 EOS** | IAPWS-IF97 |
| **天然气 EOS** | GERG-2008 |
| **界面** | 独立软件 + Excel 插件 + Python/C++ 接口 |
| **精度** | < 0.5% 全温压 |

### 3.3 REFPROP Python 调用

```python
# 必须先装 REFPROP + pypenthouselib
from pypenthouselib import REFPROP

# 初始化
rp = REFPROP("/path/to/refprop/")
# 设流体
rp.SetFluid("CO2")

# 查询临界点
qc = rp.QCrit()
print(f"T_c = {qc[0]} K, P_c = {qc[1]} MPa")

# 单点查性质(30 MPa, 280°C)
T = 553.15     # 280°C
P = 30e6       # Pa

T_sat = rp.Sat_Temp(T)
state = rp.State(T=T, P=P)
print(f"ρ = {state('D')}")
print(f"h = {state('H')} J/kg")
print(f"s = {state('S')} J/(kg·K)")
print(f"Z = {state('Z')}")
```

### 3.4 REFPROP 的具体应用场景

**适合:**
- 国家级科研项目
- 工艺包必备的"工业级物性库"
- 标准物性数据(论文、国防)
- CO₂ 制冷 / 发电 / 萃取 精确仿真

**不适合:**
- 小试 / 教学 / 速度要求高的场景
- 预算受限的工程(用 CoolProp 替代)

---

## 四、CoolProp(女王主用)

### 4.1 项目简介

**CoolProp**(开源热物性库)

**开发者:** Ian Bell(Universidad de la República,乌拉圭)
**版本:** CoolProp 6.x / 8.x
**类型:** 开源(MIT 许可证)
**网址:** www.coolprop.org

### 4.2 CoolProp 支持的流体数

| 项目 | 数值 |
|------|------|
| 流体总数 | 136 种 |
| 状态方程数 | 17 种(含 SRK、PR、SW、IF97、GERG 等)|
| 跨平台 | Windows / Linux / macOS |
| 编程语言 | C++ / C# / Python / MATLAB / Octave / Java / Ruby |
| 安装方式 | pip / conda / brew / apt |

### 4.3 CoolProp 默认对 CO₂ 的 EOS

**CoolProp 默认对 CO₂ 调用:**
- **Span-Wagner 1996**(关键)
- 误差 < 0.1%
- 与 REFPROP 等价

### 4.4 CoolProp 安装(女王已装)

```bash
# 已安装 CoolProp v8.0.0 in /home/hermes-admin/venv/
# 验证:
/home/hermes-admin/venv/bin/python -c "import CoolProp; print(CoolProp.__version__)"
# 输出:'8.0.0'

# 调用
from CoolProp.CoolProp import PropsSI
```

### 4.5 CoolProp 常用查询模式

```python
from CoolProp.CoolProp import PropsSI

# 模式 ① T, P 输入 → 输出所有物性
T = 553.15     # K(280°C)
P = 30e6       # Pa(30 MPa)
fluid = 'CO2'

ρ  = PropsSI('D',  'T', T, 'P', P, fluid)      # 密度 kg/m³
h  = PropsSI('H',  'T', T, 'P', P, fluid)      # 焓 J/kg
s  = PropsSI('S',  'T', T, 'P', P, fluid)      # 熵 J/(kg·K)
Cp = PropsSI('C',  'T', T, 'P', P, fluid)      # 定压热容 J/(kg·K)
Z  = PropsSI('Z',  'T', T, 'P', P, fluid)      # 压缩因子
μ  = PropsSI('V',  'T', T, 'P', P, fluid)      # 黏度 Pa·s
k  = PropsSI('L',  'T', T, 'P', P, fluid)      # 热导率 W/(m·K)

# 模式 ② T, P 输入 → 导出状态
phase = PropsSI('Phase', 'T', T, 'P', P, fluid)
print(f"phase: {phase}")

# 模式 ③ 饱和温度
T_sat = PropsSI('T', 'P', P, 'Q', 0, fluid)

# 模式 ④ 临界参数
T_c = PropsSI('Tcrit', fluid)
P_c = PropsSI('Pcrit', fluid)
ρ_c = PropsSI('Dcrit', fluid)
```

### 4.6 CoolProp 支持的流体列表(女王常用)

| 流体名 | 适用场景 |
|--------|----------|
| **CO₂** | 超临界萃取、CCS、制冷 |
| **H₂O**(Water)| 水蒸气、过程蒸汽 |
| **Air** | 空气相关计算 |
| **N₂** | N₂ 储罐、低温保护 |
| **O₂** | 氧化剂、燃烧 |
| **H₂** | 氢气、燃料电池 |
| **CH₄** | 天然气、燃料 |
| **C₂H₆ / C₃H₈ / C₄H₁₀** | 烃类(LPG)|
| **C₆H₁₄**(n-Hexane)| 烃类 |
| **C₆H₆**(Benzene)| 有机溶剂 |
| **CH₃OH**(Methanol)| 醇类 |
| **C₂H₅OH**(Ethanol)| 醇类 |
| **NH₃** | 制冷剂 |
| **SO₂** | 烟气处理 |

**完整名单在:** http://www.coolprop.org/fluid_properties/PureFluids.html

---

## 五、JANAF 热化学表

### 5.1 主表与查询路径

**JANAF(Joint Army-Navy-Air Force Thermochemical Tables)**

**历史:** 1960 年代起,美军出版的标准化学热力学数据表
**现在:** NIST 维护更新

**网址:** https://janaf.nist.gov/

### 5.2 JANAF 提供的数据

| 数据 | 单位 | 备注 |
|------|------|------|
| Cp° | J/(mol·K) | 标准态定压热容 |
| S° | J/(mol·K) | 标准态熵 |
| H° − H°₀ | kJ/mol | 显热(从 0 K 起到指定 T)|
| ΔH°f | kJ/mol | 标准生成焓 |
| ΔG°f | kJ/mol | 标准生成 Gibbs 自由能 |
| log K_f | — | 生成反应 log K |

### 5.3 JANAF 适用场景

**反应热计算 + 平衡常数 + 多变温热力学:**
- 燃烧反应焓
- 重整反应平衡
- 相变焓 + 反应焓结合

**女王工程:** 反应器热平衡、反应条件优化、工艺热集成

### 5.4 CO₂ 在 JANAF 中的数据

| T (K) | Cp° (J/mol·K) | S° (J/mol·K) | H° − H°₀ (kJ/mol) |
|-------|-----------------|----------------|--------------------|
| 298.15 | 37.135 | 213.785 | 9.354 |
| 500 | 44.626 | 244.685 | 17.679 |
| 800 | 54.308 | 280.701 | 34.530 |

**数据来源:** NIST-JANAF 表

---

## 六、DIPPR 数据库

### 6.1 主表与查询路径

**DIPPR(American Institute of Chemical Engineers Design Institute for Physical Property Data)**

**网址:** aiche.org/dippr/

**主要数据:**
- 1440 种常用工业物质
- 49 项物性数据
- 物性随温度的拟合系数

**价格:** 商业(AIChE 会员免费,非会员数百美元/年)

### 6.2 DIPPR 数据类型

| 数据 | 单位 | 备注 |
|------|------|------|
| 分子量 M | g/mol | — |
| 临界参数 T_c, P_c | K, bar | — |
| 正常沸点 T_b | K | — |
| 标准生成焓 ΔH°f | kJ/mol | — |
| 标准吉布斯自由能 ΔG°f | kJ/mol | — |
| 蒸气压拟合系数 | — | Antoine 形式 |
| Cp_liq 拟合系数 | — | 每种物质 4~6 个 |
| Cp_vap 拟合系数 | — | |
| 密度拟合系数 | — | rho_liq(T)|
| 黏度拟合系数 | — | mu_liq(T)|
| 热导率拟合系数 | — | k_liq(T), k_vap(T)|
| 表面张力拟合系数 | — | |
| 汽化焓拟合系数 | — | ΔH_vap(T)|

### 6.3 DIPPR 拟合形式

**临界参数 T_c, P_c, V_c:** 直接查
**沸点 T_b:** 直接查

**温度依赖物性(拟合多项式):**
```
Cp = A + B·T + C·T² + D·T³ + E·T⁴
ρ = A · B^(-(1-T/C)^n)
μ = exp(A + B/T + C·lnT + D·T^n)
k = A + B·T + C·T² + D·T³
ΔH_vap = A · (1 - T/T_c)^(B + C·T + D·T²)
```

**实用价值:** 用 DIPPR 拟合系数可以**手算物性**,不必依赖数据库。

### 6.4 女王工程 vs DIPPR

| 场景 | DIPPR vs CoolProp |
|------|---------------------|
| **常用物质(CO₂, H₂O, N₂, ...)** | CoolProp 优先(DIPPR 也行)|
| **非标物质(界面活性剂等)** | DIPPR 优先 |
| **需要 T 依赖多项式拟合** | DIPPR(提供系数)|
| **多组分查表** | DIPPR + CoolProp |
| **国家级别标准** | DIPPR(商业权威)|

---

## 七、其他重要数据源(列名)

### 7.1 Thermopedia

**网址:** thermopedia.com
**特点:** 在线热力学百科,工程热物性查询
**适用:** 工程师快速查表

### 7.2 Engineering ToolBox

**网址:** engineeringtoolbox.com
**特点:** 简明物性表 + 计算器
**适用:** 粗算、教学

### 7.3 NIST TDE(Thermodynamic Data Engine)

**网址:** trc.nist.gov/tde.html
**特点:** NIST 内部数据库,混合物 VLE + k_ij
**适用:** PR EOS 二元交互参数查询

### 7.4 DECHEMA VLE Data Collection

**网址:** dechema.de
**特点:** 8000+ 体系的 VLE 测量数据
**适用:** 二元交互参数 k_ij 的金标准查询

### 7.5 Perry's Chemical Engineers' Handbook

**特点:** 经典工程手册,关键物质物性表
**适用:** 工艺工程师必备参考

---

## 八、女王工程的具体查表路径(按介质)

### 8.1 女王当前 scCO₂-PET 工艺 — 查表清单

| 介质 | 查表源 | 数据 | 用途 |
|------|--------|------|------|
| **CO₂** | **CoolProp / NIST WebBook** | ρ, h, s, Cp, Z | 反应器 + 减压脱气 |
| **EG**(乙二醇)| **DIPPR + NIST WebBook** | T_b, ρ, ΔH_vap, Cp | 收集罐物性 |
| **DEG** | **DIPPR + NIST WebBook** | T_b, ρ, ΔH_vap, Cp | 副产物理 |
| **H₂O** | **IAPWS-IF97 / DIPPR** | 全套 | 反应副产物 |
| **PTA** | **DIPPR** | T_m, ΔH_fus | 反应物(固体)|
| **BHET** | **NIST WebBook**(可能没有)| — | 实验数据 |
| **PET** | **DIPPR**或实验 | — | 产物 |
| **H₂** | **DIPPR** | — | 还原反应 |
| **N₂** | **CoolProp / DIPPR** | — | N₂ 封 |
| **空气** | **CoolProp / IAPWS** | — | 伴热散热 |

### 8.2 Quick Reference — 一句话查表路径

| 想算什么? | 第一查 |
|-----------|--------|
| CO₂ 物性 | CoolProp(免费)或 NIST WebBook |
| 水/蒸汽 | IAPWS-IF97 |
| 关键物质 T_c, P_c, ω | Reid 附录 A |
| Cp(T) 拟合多项式 | NIST Shomate / DIPPR 拟合系数 |
| 标准生成焓 / 燃烧焓 | JANAF / NIST WebBook |
| 二元交互参数 k_ij | NIST TDE / DECHEMA |
| 高压 蒸汽 / 超临界工况 | NIST WebBook + REFPROP |
| 工业介质物性全套 | DIPPR(商业)|

---

## 九、CoolProp 与 NIST WebBook 的协调使用

### 9.1 女王工程标准流程(新项目启动)

```
新项目 → 介质清单
   │
   ↓
常用介质(CO₂, H₂O, N₂, CH₄, ...)
   ↓
   查 CoolProp 函数清单 → 一键编程
   ↓
   自动获得 ρ, h, s, Cp, Z

新物质(特殊工艺物质)
   ↓
   查 NIST WebBook → 看是否有数据
   ↓
   无 → 查 DIPPR / Reid 附录 A
   ↓
   仍无 → 查 NIST TDE 或实验数据

全部流程验收:
   ↓
   用 NIST 实验数据 或 REFPROP 校核关键点
```

### 9.2 女王工程错误防范

| 错误 | 防范 |
|------|------|
| 拍脑袋用物性值 | **任何物性必查 CoolProp / NIST** |
| 不知道物质是不是临界点附近 | **查询临界 + 检查 T_r, P_r** |
| 实验数据 vs 计算数据混淆 | **写文档明确"用 EOS + 校核数据"** |
| 用混合物的"简单平均"代替 PR EOS | **用 CoolProp + 混合规则** |

---

## 十、本文件的边界

**本文件覆盖:**
- 五大数据源(NIST / REFPROP / CoolProp / JANAF / DIPPR)详尽介绍
- 女王工程最常用的查询模式 + CoolProp 代码示例
- 介质类型 → 数据源的快速查找路径
- 女王当前工艺的具体查表清单

**本文件不覆盖:**
- SRK / PR / SW EOS 公式 → 前面 3 个文件
- EOS 选择决策 → `when-to-use-which-eos.md`
- Python 编程实战 → `eos-python-coding.md`

---

## 十一、版本与修订

| 版本 | 日期 | 主要内容 |
|------|------|----------|
| v1.0 | 2026-06-30 | 初版。NIST / REFPROP / CoolProp / JANAF / DIPPR 全介绍 + CoolProp 编程示例 + 女王工艺查表清单。 |
