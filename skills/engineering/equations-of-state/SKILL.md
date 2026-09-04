---
name: equations-of-state
description: >
  化工热力学状态方程(EOS)选型与应用工具 skill。覆盖立方型 EOS(SRK、PR)与
  多参数 Helmholtz EOS(Span-Wagner for CO₂、IAPWS-IF97 for water、GERG-2008
  for natural gas)三大体系的公式、参数、误差、适用工况、EOS 选择决策树,
  以及 NIST WebBook / REFPROP / CoolProp / JANAF / DIPPR 数据源查找路径。
  不绑定特定项目,适用于所有化工/石化项目的物性计算与状态方程选型。
  通用工具 skill,与 valve-piping-arrangement、pump-selection-design 平级。

  当用户问"用哪个 EOS / SRK PR SW 怎么选 / 临界点附近用谁 / 工程 EOS 推荐 /
  π 值怎么算 / Z 因子怎么求 / NIST 哪里查 CO₂ 数据 / REFPROP vs CoolProp"时
  自动加载本 skill。
---

# 状态方程(EOS)选型与应用

> **本 skill 是工艺专业下面的通用工具 SKILL**(与 valve-piping-arrangement、
> pump-selection-design 平级),用于所有化工/石化项目的物性计算与状态方程选型,
> **不绑定特定项目**。
>
> **核心定位**:物性计算是化工设计的"地基",状态方程选择错误等同于计算全废。
> 本 skill 用**铁律 + 公式速查 + 决策树 + 反例**的形式,让女王任何项目涉及 EOS
> 选择时**先调本 skill 再下笔**。

---

## 一、核心铁律(8 条,违反必出问题)

### 铁律 1:任何热力学状态变化,理想气体假设只作基准,真实流体必须用真实 EOS

**依据**:经典热力学教材(Smith Van Ness Abbott 第 7 版 第 3 章)+ van der Waals 1873。

**含义**:
- 理想气体假设(Δh = ∫Cp dT, Z = 1)**只是推导起点**,不是工程精度起点
- 工程上**任何压力计算、流体性质、热力学量变**必须用真实 EOS
- 真实 EOS ≠ 理想气体:差值就是分子间作用力的体现

**反例**:
- ❌ "30 MPa, 31°C CO₂（临界点附近 ±5%）用 PR/SRK 立方型 EOS 算 h"——临界 ±5% 范围内立方型 EOS 误差可达 20%+（详见铁律 3）
- ❌ "4 MPa 饱和液 EG 的密度用 1/v = ρ" 拍脑袋——误差可达 10~20%
- ✅ **任何工程计算必须用真实 EOS,且必须明确指定 EOS 类型**

### 铁律 2:立方型 EOS(SRK/PR)用于工艺计算,多参数 EOS(SW)用于精确计算

**依据**:PR EOS 自 1976 年起为 Aspen / ProMax / CHEMCAD 默认 EOS;SW EOS 为 NIST 标准(REFPROP 默认)。

**含义**:
- **立方型 EOS 优势**:3 个参数(T_c, P_c, ω),编程简单,工程中 5~10% 误差可接受
- **多参数 EOS 优势**:~580 项多项式拟合,误差 < 0.5%,但编程复杂、依赖数据库
- **不能混用**:不能"大致用 SW"或"严格用 PR"——按精度需求选

**反例**:
- ❌ P&ID 写"EOS = Ideal Gas"——所有密度粘度流量都按气体算,液体工况偏差大
- ❌ 国家级数据用 PR EOS 算——5% 误差不符合国家标准要求
- ✅ **明确标注 EOS 类型**,且按计算目的匹配精度

### 铁律 3:临界点附近(± 5%)务必用 SW / REFPROP,其他 EOS 误差爆炸

**依据**:Span-Wagner 1996 原文对 CO₂ 临界点附近精度的实测数据(密度误差 < 0.05%)。

**含义**:
- **临界点附近(温度 ± 5% 内、压力 ± 5% 内)** 所有立方型 EOS 误差爆炸(可达 20%+)
- 此时必须用 SW / REFPROP(CoolProp 调用 SW EOS)
- 工艺常用临界点附近:CO₂ 超临界、蒸汽轮机、工质制冷剂

**反例**:
- ❌ 超临界 CO₂ 工况用 PR EOS 算密度——临界点附近偏差巨大
- ❌ 蒸汽轮机仿真用 RK EOS——临界点附近不可用
- ✅ **"临界 ± 5% 法则":一律上 SW / REFPROP**

### 铁律 4:EOS 系数(T_c, P_c, ω)来自实验测量,不要拍脑袋

**依据**:Reid Prausnitz Poling《The Properties of Gases and Liquids》第 5 版附录 A。

**含义**:
- T_c, P_c, ω 三个参数**都来自实验测量**(气液相消失的温度、压力、蒸汽压数据)
- 不允许拍脑袋、估算或类比用其他物质代替
- 工程遇到不熟悉的物质,**先查 NIST WebBook / DIPPR / Reid 附录 A**

**反例**:
- ❌ 工艺新物质没有物性,类比相似物质用其 T_c——结果蒸汽压计算大错
- ❌ 文献报道的 T_c 与 NIST 不一致——以 NIST 为准
- ✅ **NIST WebBook 优先,DIPPR 表为次,Reid 附录 A 为三**

### 铁律 5:压缩因子 Z 是 EOS 应用的第一入口

**依据**:热力学基础定义 Z = PV/(nRT),所有 EOS 都旨在精确预测 Z。

**含义**:
- **第一入口**:输入 T, P → 输出 Z → 输出 v(摩尔体积)
- Z 反应了偏离理想气体程度:
  - **Z = 1**:理想气体(高温低压极限)
  - **Z < 1**:排斥力主导(典型常温高压气体)
  - **Z > 1**:排斥力 + 热激发(典型高温低压气体)
- **Z 是其他物性计算的总钥匙**:h, s, u, f, φ 都可以从 Z 推出

**反例**:
- ❌ 工艺计算不查 Z,直接拍 ρ——可能错 50%
- ❌ 用 Z 沿路积分得到 h 而用理想气体公式算其他——不一致
- ✅ **任何 EOS 应用的起点都是先算 Z**

### 铁律 6:混合物用混合规则,二元交互参数 k_ij 必须查表

**依据**:Smith Van Ness Abbott 第 7 版第 10 章;Walas《Phase Equilibria in Chemical Engineering》。

**含义**:
- 单组分 EOS 用 T_c, P_c, ω;**混合物要用混合规则**(Van der Waals one-fluid)
- 立方型 EOS 混合规则:
  - a_mix = ΣΣ x_i x_j √(a_i a_j) (1 - k_ij)
  - b_mix = Σ x_i b_i
- **二元交互参数 k_ij 必须查表**(DECHEMA VLE 数据集有,REFPROP 有内置)

**反例**:
- ❌ k_ij 不查表,假设为 0——多组分物性错 5~15%
- ❌ 强极性混合物(醇+水)用普通 PR 混合规则——精度不够
- ✅ **强极性系统用电解质 / SAFT / COSMO-RS 等专门模型**

### 铁律 7:校核用 NIST REFPROP 实验数据,不要用 EOS 自身结果自校

**依据**:实验物性数据的精度通常高于 EOS 预测,这是验证 EOS 精度的标准做法。

**含义**:
- 计算完成后,**用 NIST REFPROP 实验数据校核**:
  - 同 T, P 下 REFPROP 输出的 ρ, h, s 与自己结果对照
  - 偏差应 < EOS 标称误差(SRK 5%, PR 3%, SW 0.5%)
- **不校核会导致技术差错**:EOS 可能跑得"很顺"但物理结果错

**反例**:
- ❌ EOS 算完直接画图,不校核——错误累积到下游
- ❌ 用 NIST 不同 T, P 的值与 EOS 计算同 T, P 对比——错位对比无效
- ✅ **逐点(P, T 网格)对比 REFPROP 实验数据**

### 铁律 8:PFD / P&ID 必须明确标注 EOS 选择——Aspen 默认不一定是工程想要

**依据**:Aspen 默认 PR EOS + 不同物性数据包;具体工况可能需要 SW 或 PC-SAFT。

**含义**:
- **任何工艺包 / 数据表必须明确标注**:
  - 选用 EOS 类型(SRK / PR / SW / 其他)
  - 物性数据库来源(NIST / DIPPR / DBxxxx)
  - 二元交互参数来源(DECHEMA / 实验)
- **Aspen 默认是 PR + DB 物性库,不等于工程最优**

**反例**:
- ❌ "用 Aspen 默认"——文档不明确,日后审计困难
- ❌ 用 Aspen 默认 + 校核实验数据不一致——未明确哪个为准
- ✅ **EOS 选择的依据 + 文档明确写明**

---

## 二、概念层(3 个核心概念)

### 2.1 EOS 是什么?

**EOS(Equation of State) = 状态方程**

> 热力学定义:**描述平衡态系统宏观状态变量(P, V, T, n)之间定量关系的方程。**

**EOS 的真正作用**:输入 T, P → 输出所有热力学性质。

| 输出 | 公式(从 EOS 导出) |
|------|---------------------|
| 摩尔体积 V_m | 解 EOS 方程 |
| 压缩因子 Z | Z = PV_m / RT |
| 密度 ρ | 1 / V_m × M |
| 焓 h | h = h° + ∫Cp dT + h^R |
| 熵 s | s = s° + ∫Cp/T dT + s^R |
| 逸度 f | ln(f/P) = ∫(Z-1)/P dP |
| 逸度系数 φ | φ = f/P |
| 定压热容 Cp | EOS 二次求导 |

### 2.2 理想气体 vs 真实流体

| 特征 | 理想气体 | 真实流体 |
|------|----------|---------|
| 状态方程 | PV = nRT | f(P, V, T) = 0(EOS 形式)|
| 分子模型 | 无体积、无吸引力 | 有体积、有吸引力 |
| 适用条件 | 高温低压极限 | 任何状态 |
| 误差 | 10~50%(典型工程)| 2~10%(立方型)< 0.5%(多参数)|

**关键物理**:真实气体有**分子体积**(排斥力,反映为 a, b)和**分子间吸引力**(反映为 a 项),所以 Z ≠ 1。

### 2.3 立方型 EOS vs Helmholtz 多参数 EOS

| 项 | 立方型 EOS | Helmholtz 多参数 EOS |
|----|-----------|----------------------|
| **形式** | P = f(V, T)(V 出现在 3 次)| A = f(T, ρ)(亥姆霍兹自由能)|
| **参数** | 3 个(T_c, P_c, ω)| T_c, ρ_c + ~30~580 项多项式系数 |
| **精度** | 5~10%(临界点差)| < 0.5%(全温压范围)|
| **编程** | 简单(立方方程求根)| 复杂(多项式 + 指数项)|
| **典型代表** | vdW, RK, SRK, PR | SW(CO₂), IAPWS-IF97(蒸汽), GERG-2008 |
| **常用软件** | Aspen, ProMax, CHEMCAD | REFPROP / CoolProp |

---

## 三、公式速查(三大 EOS 一图速查)

### 3.1 SRK EOS(Soave-Redlich-Kwong,1972)

```
              RT              a(T)·α
    P = ──────────  −  ──────────────
          (V − b)          V(V + b)
```

**参数:**
```
a(T) = a_c × α(T)
α(T) = [1 + m·(1 − √(T_r))]²
m    = 0.48 + 1.574·ω − 0.176·ω²
a_c  = 0.42747·R²·T_c² / P_c
b    = 0.08664·R·T_c / P_c

T_r = T / T_c

ω:偏心因子(acentric factor,反映分子不对称度)
```

### 3.2 PR EOS(Peng-Robinson,1976)

```
              RT                  a(T)
    P = ──────────  −  ─────────────────────
          (V − b)          V² + 2bV − b²
```

**参数:**
```
a(T) = a_c × α(T)
α(T) = [1 + κ·(1 − √(T_r))]²
κ    = 0.37464 + 1.54226·ω − 0.26992·ω²
a_c  = 0.45724·R²·T_c² / P_c
b    = 0.07780·R·T_c / P_c
```

**PR 与 SRK 的差别:**
- V 出现在 V² + 2bV − b²(分母),而 SRK 是 V(V+b)
- **PR 对液体密度预测更好**(临界压缩因子 Z_c = 0.307 vs SRK 0.333)
- **工业首选**(Aspen / ProMax 默认)

### 3.3 SW EOS(Span-Wagner,1994 for CO₂)

**完全不同的形式——基于 Helmholtz 自由能:**
```
A(T, ρ)      A^ideal(T, ρ)    A^R(T, ρ)
───────── = ─────────────── + ────────────
  R·T           R·T              R·T

δ = ρ / ρ_c      对比密度
τ = T_c / T      对比温度倒数

A^R(δ, τ)   =  Σᵢ₌₁ᴺ nᵢ·δ^dᵢ·τ^tᵢ                   (多项式项)
            +  Σⱼ₌₁ᴹ nⱼ·δ^dʲ·τ^tʲ·exp(−δ^cʲ)        (指数项)
```

**CO₂ 的 SW EOS:**
- **~580 项多项式系数**
- 适用范围:216~1100 K, 0~800 MPa
- **密度误差 < 0.05%**(三相点以外)
- 国家级标准(NIST CO₂ 标准)

---

## 四、EOS 适用精度速查表

| EOS | 等温相区 | 临界点附近 | 液相密度 | 二元 VLE | 气体密度 | 编程难度 |
|-----|----------|------------|-----------|-----------|-----------|----------|
| **vdW** | △ 粗 | ✗ 不用 | △ | ✗ | △ | 简单 |
| **RK** | ✓ 中 | ✗ 不用 | △ | △ | ✓ | 简单 |
| **SRK** | ✓ 中 | △ | ✓ | ✓ | ✓ | 简单 |
| **PR** | ✓ 中 | △ | ✓✓ | ✓ | ✓ | 简单 |
| **SW** | ✓✓ 精 | ✓✓ | ✓✓ | ✓✓ | ✓✓ | 复杂 |
| **IAPWS-IF97** | ✓✓ 精 | ✓✓ | ✓✓ | ✓✓ | ✓✓ | 中等 |
| **GERG-2008(混合)**| ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | 复杂 |

(✓✓ 优秀、✓ 良好、△ 可用、✗ 不用)

---

## 五、EOS 选择决策树(速查)

```
是否需要计算热力学性质?
├── 否 → 用现成数据表(NIST WebBook / DIPPR)
└── 是 → 用什么 EOS?
        ├── 已知具体物质 + 临界点附近
        │   └── CO₂ / 蒸汽 / 天然气?
        │       ├── CO₂ → Span-Wagner EOS(REFPROP / CoolProp 默认)
        │       ├── 蒸汽 → IAPWS-IF97
        │       └── 天然气 → GERG-2008
        ├── 混合物 VLE 计算(精度要求一般)
        │   └── 立方型 EOS(PR 首选)
        ├── 单一物质 + 远离临界点
        │   └── PR EOS + NIST 实验数据校核
        └── 教学 / 示意
            └── SRK EOS(简单清晰)
```

---

## 六、数据源与查表路径(女王速查)

| 数据类型 | 第一权威 | 次选 | 备注 |
|----------|----------|------|------|
| **CO₂ 全温压性质** | NIST WebBook / REFPROP | CoolProp(开源) | SW EOS,精度最高 |
| **CO₂ T_c, P_c, ω** | NIST WebBook | Reid 附录 A | 7.38 MPa, 31.1°C, ω = 0.225 |
| **常用物质 T_c, P_c** | Reid Prausnitz Poling 附录 A | DIPPR DB | 实验值优先 |
| **Cp(T) 拟合系数** | NIST WebBook(Shomate 方程)| JANAF 表 | 用于显热积分 |
| **二元交互参数 k_ij** | DECHEMA VLE DB | REFPROP 内置 | 混合物关键 |
| **标准生成焓 ΔH°f** | CODATA / NIST WebBook | JANAF 表 | -393.52 kJ/mol(CO₂)|
| **汽化焓 ΔH_vap** | NIST WebBook | DIPPR DB | 随温度变化 |

---

## 七、与其他子 SKILL 的关系

| SKILL | 关系 |
|-------|------|
| `valve-piping-arrangement` | 阀门选型常涉及 CO₂ / 烃类物性,EOS 由本 SKILL 提供 |
| `petrochem-process-design` | 母 skill,工艺流程 + 反应器设计 + 物性都遵循本 SKILL 的 EOS 选择 |
| `tank-n2-blanket-design` | 储罐 N₂ 封涉及临界点附近 CO₂ 物性,用 Span-Wagner EOS |
| `pump-selection-design` | 泵的黏度密度计算需要 EOS |
| `design-institute-pid` | P&ID 上 EOS 选择标注规范 |
| `pressure-vessel-expert` | 压力容器设计压力用 EOS 算出蒸汽压 |
| `pid-pfd-v69-standards` | PFD 上的 P-T 节点状态用 EOS 标注 |

---

## 八、调用时机(自动加载 vs 手动查询)

**自动加载**(女王未明说但属于本 skill 范畴):
- 工艺计算涉及临界点附近物性
- 反应器 + 减压脱气设计
- 制冷循环 / CO₂ 循环 / 蒸汽循环设计
- 任何"输入 T, P 输出物性"请求
- 出现"用哪个 EOS / 选 SRK 还是 PR / 多参数 EOS"类问题

**手动查询**:
- "CO₂ 在 30 MPa, 280°C 的密度是多少"
- "临界点附近用什么 EOS"
- "SRK 与 PR 选哪个"
- "Span-Wagner EOS 是什么"
- "哪里找 ΔH°f / ΔH_vap 数据"

---

## 九、知识库溯源

| 铁律编号 | 主要依据 | 章节定位 |
|----------|----------|----------|
| 铁律 1 | Smith Van Ness Abbott(第 7 版)| 第 3 章 Residual Properties |
| 铁律 2 | Peng-Robinson (1976) 原始论文 | Ind. Eng. Chem. Fundam. 15(1) |
| 铁律 3 | Span-Wagner (1996) 原文 | J. Phys. Chem. Ref. Data 25(6)|
| 铁律 4 | Reid Prausnitz Poling(第 5 版)| 附录 A |
| 铁律 5 | 经典热力学教材 | 第 3 章 热力学基本关系 |
| 铁律 6 | Walas《Phase Equilibria》 | 混合规则章节 |
| 铁律 7 | NIST REFPROP 文档 | 数值方法学 |
| 铁律 8 | 工程包规范文档惯例 | — |

**声明**:本 SKILL 不覆盖"如何用剩余性质法计算具体焓值/熵值"——这是状态方程的**下游应用方法**,由工艺专业单独技能承担。本 SKILL 专注于**状态方程本身的公式、选型、数据源**。

---

## 十、文件结构

```
equations-of-state/
├── SKILL.md                              # 本文件(8 铁律 + 公式速查 + 决策树)
└── references/
    ├── ideal-gas-baseline.md             # 理想气体基线 + 修正必要性
    ├── srk-eos-detailed.md               # SRK 1972 推导、公式、参数表、CO₂ 算例
    ├── pr-eos-detailed.md                # PR 1976 公式 + 与 SRK 对比 + 编程示例
    ├── span-wagner-eos-detailed.md       # SW 1994 多参数 Helmholtz 详解 + CO₂ 应用
    ├── cubic-vs-multi-param.md           # 立方型 vs 多参数的本质差别
    ├── when-to-use-which-eos.md          # EOS 选择决策树(按工况/物质/精度)
    ├── data-sources-and-references.md    # NIST/JANAF/DIPPR 数据源查找路径
    └── eos-python-coding.md              # Python 编程示例(CoolProp / 自实现 PR)
```

---

## 十一、版本与修订

| 版本 | 日期 | 主要内容 |
|------|------|----------|
| **v1.0** | 2026-06-30 | 初版。8 铁律 + 概念 + 公式速查 + EOS 选择决策树 + 数据源。源由:女王询问状态方程三大类(SRK、PR、SW)的具体公式 + EOS 概念 + 剩余性质法的数据来源;女王确认除"剩余性质法"外,其他建档。本 skill 作为工艺专业下面通用工具子 SKILL。 |
