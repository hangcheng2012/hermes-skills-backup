---
title: Aspen 胺液脱硫脱碳工艺模拟综合参考
description: |
  涵盖 MDEA / DEA / MEA / K₂CO₃ / Hot Potassium Carbonate 等体系的 Aspen Plus
  化学反应输入、EQUIL vs KINETIC 判据、Rate-Based 操作、动力学参数溯源
  （k=4.32e13, E=13.249 kcal/mol 的来源）。
date: 2026-08-07
sources:
  - AspenTech (2008) Rate-Based Model of CO2 Capture by NaOH
  - Pinsent, Pearson & Roughton (1956) Trans. Faraday Soc. 52:1512
  - Hikita et al. (1976) Kagaku Kogaku Ronbunshu 2:233
  - Austgen, Rochelle, Peng, Chen (1989) AIChE J. 35(11):1754-1765
  - Pohorecki & Moniuk (1988) Chem. Eng. Sci. 43(7):1677-1684
  - 女王 Aspen 截图核验 + web 文档交叉核验 (PMC9178620 / DiVA / Polimi / Chalmers)
keywords: [MDEA, 胺液, Rate-Based, EQUIL/KINETIC, Enhancement Factor, Pinsent, AspenTech 2008, K2CO3, MEA, DEA, Hatta]
related_file: petrochem-process-design/SKILL.md
---

# Aspen 胺液脱硫脱碳工艺模拟综合参考

> **用途**：以后查询 Aspen 模拟胺液吸收塔/再生塔的化学反应输入、Rate-Based 设置、动力学参数溯源时，直接打开本文件即可。
>
> **整合源**：来自与 J.A.R.V.I.S. 的对话（2026-08-07），基于女王 Aspen 截图 + 公开文献核验。

## 目录

1. [角色定位](#1-角色定位)
2. [触发条件](#2-触发条件)
3. [必查 5 大铁律](#3-必查-5-大铁律)
4. [MDEA 标准 11 反应清单](#4-mdea-标准-11-反应清单)
5. [EQUIL vs KINETIC 判据](#5-equil-vs-kinetic-判据)
6. [Rate-Based 5 步操作](#6-rate-based-5-步操作)
7. [动力学参数溯源](#7-动力学参数溯源)
8. [联动规则与失败模式](#8-联动规则与失败模式)

---

## 1. 角色定位

工艺工程师在 Aspen Plus 中搭建胺液吸收塔/再生塔的 RadFrac 反应吸收模型时，会遇到三类共性问题：

1. **反应集怎么填**：标准反应集（MDEA 11 反应、MEA 8 反应、K₂CO₃ 6 反应）的每一项应该选 EQUIL 还是 KINETIC？
2. **Reaction type 选什么**：表单默认是 Power Law，但电解质反应必须改成 ELECTRL / ACIDS / AMINES / MDEA——这是什么？什么时候用哪个？
3. **Rate-Based 模式下怎么改**：切到 Rate-Based 后，反应模板自动转为增强因子算法；Bulk/Film Reactions 标签里需要复核哪些项？E=1 为什么是错的？

本参考文档给出这三大问题的**可复用判断准则、操作步骤、参数溯源**。

---

## 2. 触发条件

| 女王动作 | 自动加载（按 description 关键词匹配）|
|---------|----------------------------------|
| 问"胺液吸收塔/再生塔的化学反应怎么输入 Aspen" | 整个文档加载 |
| 问"MDEA / DEA / MEA 工艺的反应集如何写" | 第 4 章 |
| 问"Rate-Based 模式下反应集如何重新设置" | 第 6 章 |
| 问"k、Ea 的值是从哪里来的"（溯源/合规审计）| 第 7 章 |
| 问"EQUIL 还是 KINETIC 怎么选" | 第 5 章 |
| 上传 Aspen 截图含 Reactions / Kinetic / Equilibrium / Film Reactions 标签 | 全文检索 |
| 涉及 MDEA、aMDEA、活化 MDEA、Benfield、Benfield-MDEA、HiPure 工艺 | 全文 |

---

## 3. 必查 5 大铁律

### 铁律 1：电解质反应**永远不要用 Power Law 默认**

Aspen 反应集默认 Reaction type 是 Power Law（幂律 k·exp(-Ea/RT)），对 MDEA / DEA / MEA / K₂CO₃ 等电解质反应**算出来不对**。

- 必须显式改：`ELECTRL`（通用电解质）/ `ACIDS`（酸气-胺）/ `AMINES`（胺类）/ `MDEA`（专用于叔胺催化 CO₂ 水合）
- 改完之后 Aspen 才会调用内置 k 数据 + Hatta 增强因子算法

### 铁律 2：电离反应**必须 EQUIL，绝不放 KINETIC**

反应 2-6 在 MDEA 集中是质子转移/电离（k ≈ 10⁸ - 10¹⁰ L/(mol·s)）。

- Reaction type 选 `INST-EQ` / `INSTANT`（瞬时平衡）
- 不进入 KINETIC → 避免 ODE 刚度问题（速率差 6 个数量级）
- 这是 Rate-Based 模型能收敛的前提条件

### 铁律 3：n = 0 是红旗

CO₂ + OH⁻ / CO₂ + 胺 反应**对 CO₂ 是 1 级**（Pinsent、Hikita、Austgen 全部按 1 级回归）。

- Aspen 官方模板默认 n = 1
- 模型文件里出现 n = 0，意味着被老版本（V7 之前）的写法继承下来，必须**主动改回 n = 1**

### 铁律 4：k、Ea 单位随 [Cᵢ] basis + Rate basis 挂钩

- 框里写的 k 值**单看大小无法判断合理性**，必须先反算到 298 K 下的等效 L/(mol·s) 再与文献对比
- 框里 E 默认单位是 **cal/mol**（不是 J/mol）——Aspen 全局 ENG units 影响
- 单位换算演示见第 7 章

### 铁律 5：Rate-Based 模式下**必查 Bulk / Film Reactions 配置**

- Aspen 默认按 Reaction type 自动选定 reaction handling，但**自动选不等于选对**
- 关键检查项：
  - 电离反应（R2-6）→ 应为 `Instantaneous`
  - 限速反应（R7, R8, R11, R12）→ 应为 `Rate-controlled with Hatta enhancement`
- **Profile 表里 E = 1.0 即提示没启用增强因子**，是错的——回去改 Reaction type

---

## 4. MDEA 标准 11 反应清单

> **出处**：AspenTech (2008) "Rate-Based Model of CO₂ Capture Process by NaOH"，后被 MDEA / MEA / K₂CO₃ / Hot Potassium Carbonate 等模板沿用。实验数据起源：Pinsent, Pearson & Roughton (1956) + Hikita et al. (1976) + Austgen et al. (1989)。

### 完整反应清单

| Rxn | 化学反应 | 类型 | Reaction type（Reaction Set）| Rate-Based 处理 | 备注 |
|-----|---------|------|-------------------------------|----------------|------|
| R1  | —（通常空缺或被删除）| — | — | — | 跳号是历史残留 |
| R2  | H₂O ⇌ H⁺ + OH⁻ | EQUIL | `INST-EQ` / `INSTANT` | Instantaneous | 水电离，k ≈ 10¹⁰ L/(mol·s) |
| R3  | HCO₃⁻ ⇌ H⁺ + CO₃²⁻ | EQUIL | `INST-EQ` | Instantaneous | 二级电离 |
| R4  | MDEA⁺ ⇌ MDEA + H⁺ | EQUIL | `INST-EQ` | Instantaneous | 质子化 MDEA 解离 |
| R5  | H₂S ⇌ HS⁻ + H⁺ | EQUIL | `INST-EQ` | Instantaneous | H₂S 一级电离 |
| R6  | HS⁻ ⇌ S²⁻ + H⁺ | EQUIL | `INST-EQ` | Instantaneous | H₂S 二级电离 |
| R7  | CO₂ + OH⁻ → HCO₃⁻ | KINETIC | `ELECTRL` / `ACIDS` | Rate-controlled (Hatta) | k = 4.32×10¹³ m³/(kmol·s)，E = 13.249 kcal/mol |
| R8  | HCO₃⁻ → CO₂ + OH⁻ | KINETIC | `ELECTRL` / `ACIDS` | Rate-controlled (Hatta) | 与 R7 配对（K_eq 自动分配） |
| R9  | （跳过）| — | — | — | 历史残留 |
| R10 | （跳过）| — | — | — | 历史残留 |
| **R11** | **MDEA + CO₂ + H₂O → HCO₃⁻ + MDEA⁺** | KINETIC | **`MDEA` / `ACIDS`** | **Rate-controlled (Hatta)** | **MDEA 法核心反应 / 限速反应** |
| R12 | HCO₃⁻ + MDEA⁺ → MDEA + CO₂ + H₂O | KINETIC | `MDEA` / `ACIDS` | Rate-controlled (Hatta) | 与 R11 配对 |

> **重要**：9、10 跳号是常见现象——早期版本里常包含 MDEA + CO₂ 两性离子（zwitterion）机理但被删除。**不影响模拟**——Aspen 按 Rxn ID 匹配，ID 不连续不会报错。

### 反应机理要点（工程师必懂）

#### 为什么 MDEA 是「叔胺催化 CO₂ 水合」而不是「直接反应」

MDEA 是叔胺（结构：HOCH₂CH₂—N(CH₃)—CH₂CH₂OH），**N 上无活泼氢** → **不能形成两性离子 zwitterion**（这是与 MEA/DEA 的本质差异）。

- → MDEA 自身不直接消耗。
- → 实际机制：**MDEA 通过质子化/去质子化（MDEA ⇌ MDEA⁺ + H⁺）传递 H⁺，把局部 pH 拉高，间接加速 CO₂ + H₂O → HCO₃⁻ + H⁺**。
- → 净反应：CO₂ + H₂O + MDEA ⇌ HCO₃⁻ + MDEA⁺
- → **MDEA 净消耗量 = 0**（在塔中穿梭），但通过反应 R11 起到"碱性催化剂"功能。

#### R11 才是限速反应

工业 MDEA 吸收塔的塔高、塔板数设计，主要由 R11 决定：

- 表观一级速率常数 k_MDEA(298) ≈ 5 - 9 L/(mol·s)
- 远小于 R7 的 CO₂ + OH⁻（k ≈ 10³ - 10⁴ L/(mol·s)）
- 但 R7 在 OH⁻ 浓度低的塔板（贫液段）受限，因此**总体限速 = R11**

#### 这也是 MDEA 选择性脱硫（H₂S vs CO₂）比 MEA 好的根源

H₂S 是质子转移瞬时反应（k ≈ 10¹⁰）→ 任何胺都被 H₂S 快速吸收
CO₂ 必须经水合（k ≈ 0.01 - 1 s⁻¹）→ 叔胺不直接参与，MDEA 不能加速 → MDEA 体系下 CO₂ 吸收速率慢，远低于 H₂S 吸收速率。

→ 这就是为什么天然气脱硫常用 MDEA（脱 H₂S 而保留 CO₂），煤化工变换气脱碳用 MDEA / MDEA + PZ。

### Red Flag 检验清单

每次拿到一个新的 MDEA 反应集 Aspen 文件，女王请按以下清单逐项核：

- [ ] **R2-R6 都是 INST-EQ**（不是 POWERLAW）
- [ ] **R7、R8 的 Reaction type 是 ELECTRL/ACIDS**（不是 Power Law）
- [ ] **R11、R12 的 Reaction type 是 MDEA 或 ACIDS**（这是模板祖宗）
- [ ] **所有反应 n ≥ 1**（CO₂ 至少是 1 级；若发现 n=0 改回）
- [ ] **k 单位已经在 Kinetics 表里**：m³/(kmol·s) for CO₂ + OH⁻、L/(mol·s) for 胺类
- [ ] **E 单位是 cal/mol**（Aspen 默认），不是 J/mol
- [ ] **T₀ 是空的**（可选）；若是填了 298 K，符合数据原始回归温度

### MEA / DEA 反应集差异提示

- **MEA 反应集**：典型 8 反应
  - 2 × 电离（H₂O, HCO₃⁻）
  - 2 × MEA 解离（MEAH⁺ ⇌ MEA + H⁺；MEACOO⁻ + H₂O ⇌ MEA + HCO₃⁻）
  - 2 × KINETIC：CO₂ + OH⁻ ⇌ HCO₃⁻（与 MDEA 相同）；**CO₂ + MEA → MEACOO⁻ + H⁺** ← **这是 MEA 限速反应，两性离子机理**
  - 2 × KINETIC 配对
- **DEA 反应集**：典型 10 反应，机理类似 MEA 但 DEA 是仲胺，两性离子机理更显著
- **K₂CO₃ 反应集**：6 反应，少胺类反应，多 K⁺ + HCO₃⁻ / CO₃²⁻ / KHCO₃ 平衡

不同反应集请按 Reaction Set 内部 Aspen 数据库自动调用的 k 数据为准，**不可混用 MDEA 的 k 到 MEA 反应**。

### 实际使用

#### 把 RMDEA 反应集从老 Aspen 模板迁到新版本

1. 打开老文件 .apw / .bkp
2. 复制 Reactions | RMDEA 整个反应集
3. 粘贴到新模型
4. 逐条核对 Reaction type（重点 R7-R12）
5. 跑初始化 + Run

#### 把 Power Law 反应改成电解质反应（迁移路径）

举例：把 R7 从 Power Law → ELECTRL

1. Data Browser → Reactions → RMDEA → 选 R7
2. Kinetics 子表 → Reaction type 列下拉 → 选 `ELECTRL` / `ACIDS`
3. 点 OK 确认；Aspen 会弹窗问"是否保留现有 k、E、n"——选 No，让它填充内置默认
4. 重新 initialize + Run

> **警告**：Aspen 内置默认对 R7 的 k、E 是 `4.32 × 10¹³ / 13.249 kcal/mol`（标准工程值），但对 R11 的内置 k（仅当 Reaction type = `MDEA` 才生效）有不同版本差异。务必对照 Project 文档或工艺包供应商数据再修改。

---

## 5. EQUIL vs KINETIC 判据

> Aspen 把反应按速率分为两类：EQUIL（瞬时平衡，无穷大速率）与 KINETIC（有限速率，由速率方程 r = k·C^n·exp(-E/RT) 控制）。
> 选错了 → 要么数值错（刚度不收敛），要么过度细化（不收敛或极慢）。

### 准则 1（核心）：看 k 相对 τ_res 的快慢

判断反应该选 EQUIL 还是 KINETIC，**只看一个物理量**：反应的速率常数 k 是否**远大于**所在反应器的特征时间倒数 1/τ_res。

$$k \cdot C_\text{limit} \gg \frac{1}{\tau_\text{res}} \quad \Rightarrow \quad \text{EQUIL}$$

$$k \cdot C_\text{limit} \sim \frac{1}{\tau_\text{res}} \quad \Rightarrow \quad \text{KINETIC}$$

其中：

- `k`：反应速率常数，单位 L/(mol·s) 或 s⁻¹（按级数而定）
- `C_limit`：限制反应物的浓度上限（mol/L）
- `τ_res`：反应器特征停留时间（s）

不同反应器的 τ_res：

- **CSTR / RCSTR**：τ = V_liq / F_liq
- **PFR / RPlug / 列管**：τ = V_liq / F_liq
- **RBatch / 间歇釜**：τ = 反应周期
- **RadFrac 反应吸收塔板**：τ = 持液量 / 液体流率（典型 1-5 s）
- **填充塔/吸收塔填料段**：τ = (持液量分数 × 塔段体积) / 液体流率

### 准则 2：典型反应速率常数数量级（经验对照）

| 反应类型 | k @ 298 K（典型量级）| 判定 |
|---------|---------------------|------|
| 强酸/强碱电离 | 10¹⁰ L/(mol·s) | **EQUIL**（瞬时）|
| H⁺ 转移（质子水合）| 10⁸ - 10¹⁰ | **EQUIL** |
| 弱酸电离（HAc、HS⁻、HCO₃⁻）| 10⁵ - 10⁷ | 一般 EQUIL（除非极高要求精度）|
| **CO₂ + OH⁻ → HCO₃⁻** | **10³ - 10⁴ L/(mol·s)** | **KINETIC**（有限速率）|
| CO₂ + 仲胺（MEA/DEA）| 10² - 10³ | KINETIC |
| **CO₂ + 叔胺（MDEA，催化路径）** | **1 - 50** | **KINETIC**（限速）|
| 酶催化 | 10⁻² - 10² | KINETIC |
| 慢有机反应 | 10⁻⁶ - 10⁻³ | KINETIC |

**粗略阈值**：

- k > 10⁶ L/(mol·s) → 一般 EQUIL
- k < 10³ L/(mol·s) → 必须 KINETIC
- k 在 10³ - 10⁶ → 看 τ_res；τ_res = 1-5 s 的塔板上，多数仍按 KINETIC 算

### 准则 3：看反应的本质（机理）

| 反应机理 | 选 EQUIL 还是 KINETIC |
|---------|---------------------|
| 质子转移、电离 | EQUIL |
| 异构化 | EQUIL（瞬时）|
| 配合物生成/解离（弱配位）| EQUIL |
| 自由基链反应 | KINETIC |
| 加氢、氧化、羰化等需要活化能的反应 | KINETIC |
| CO₂、H₂S、SO₂ 在液相中的吸收反应 | KINETIC |

> **核心理念**：EQUIL 是**热力学层面的瞬时平衡**；KINETIC 是**需要越过能垒的慢过程**。
> 电离反应、热力学极限快的反应 → EQUIL；与分子反应性直接相关的反应 → KINETIC。

### 准则 4：刚度问题（数值稳定性）

如果一个反应集里**同时存在快反应（k ≈ 10¹⁰）与慢反应（k ≈ 1）**，且都被写成 KINETIC → Aspen 会遇到**刚性（stiff）ODE 问题**——求解器（如 Gear 算法）必须在两种时间尺度间反复内插，**可能直接卡死**。

**应对**：

- 快反应必须 EQUIL
- 慢反应 KINETIC
- 让 Aspen 用**多种速率尺度的混合算法**：电离瞬时 + 有限速率 CO₂ 吸收（这就是为什么 MDEA 反应集是 2-6 EQUIL + 7-12 KINETIC）

### 准则 5：经济性 / 必要性

KINETIC 反应需要：

- 速率常数 A、Ea（或 k、ΔH‡）
- 反应级数 α、β、γ
- Rate basis + Concentration basis 单位

如果工程上**不需要评估反应动力学**（如只是做物料平衡、热平衡、公用工程计算），用 EQUIL 是最稳的选择：

- **Reaction type 改 EQUIL 后，Aspen 只需要 K_eq**（可以查数据库或 ΔG 算）
- 不需要 k、Ea、n —— 节省大半天文献调研

> **结论**：只有当目的是"反应器尺寸/持液量/塔板数/停留时间优化"时，CO₂ + 胺才必须用 KINETIC。

### MDEA 集的具体分配（示范）

按上面 5 条准则，MDEA 反应集必须按以下方式分类：

| Rxn | 反应 | k 估 | 必选类型 |
|-----|------|-----|---------|
| R2 | H₂O ⇌ H⁺ + OH⁻ | 10¹⁰ | EQUIL |
| R3 | HCO₃⁻ ⇌ H⁺ + CO₃²⁻ | 10⁷ | EQUIL |
| R4 | MDEA⁺ ⇌ MDEA + H⁺ | 10⁷ | EQUIL |
| R5 | H₂S ⇌ HS⁻ + H⁺ | 10¹⁰ | EQUIL |
| R6 | HS⁻ ⇌ S²⁻ + H⁺ | 10⁵ | EQUIL |
| **R7** | CO₂ + OH⁻ → HCO₃⁻ | 10⁴ | **KINETIC** |
| **R8** | HCO₃⁻ → CO₂ + OH⁻ | 反向 | **KINETIC** |
| **R11** | MDEA + CO₂ + H₂O → HCO₃⁻ + MDEA⁺ | 1-50 | **KINETIC**（限速）|
| **R12** | HCO₃⁻ + MDEA⁺ → MDEA + CO₂ + H₂O | 反向 | **KINETIC** |

→ **典型分布：6 反应 EQUIL，4 反应 KINETIC**（含 9、10 跳号）——这是 MDEA 集的唯一正确切法。

### 在 RadFrac Rate-Based 模式下

Rate-Based 模型对 EQUIL/KINETIC 的处理与平衡级模型不同：

- 平衡级反应只在体相内按 KINETIC/EQUIL 计算 → 不涉及液膜
- **Rate-Based 模式下反应可以发生在液膜内 + 体相内**——由"Enhanced factor E"修正

所以在 Rate-Based 模式下：

- EQUIL 反应会被放在 `Bulk | Instantaneous` 或直接跳过
- KINETIC 反应会被放在 `Bulk | Rate-controlled` + `Film | Rate-controlled with Hatta enhancement`

具体的"Film/Bulk Reactions 标签"操作详见第 6 章。

### 反直觉但正确：一对可逆反应可以分成两种类型

Aspen 允许一对可逆反应（A ⇌ B）**分别标记为 EQUIL（A）和 KINETIC（B）**——这不是错误，是**瞬时反应**与**有限速率反应**共存时的合理简化。

但要确认：

- **正逆反应都必须是 K_eq 自洽**
- 即 K_eq 正向 / K_eq 逆向 = K_eq 净反应
- 否则 Aspen 求解时会警告 "consistency error"

如果反应集里出现 K_eq 不自洽的情况，会出现：

- 模拟结果对反应进度不敏感
- 产物分布计算异常
- 这种情况下回到 EQUIL/KINETIC 重新评估

### 实战操作 SOP

1. **拿到反应集模板**：先看 Aspentech 官方模板的 Reaction type 列
2. **逐项确认** Reaction type（Power Law / ELECTRL / INST-EQ / INSTANT）
3. **如果反应是有限速率且被错写为 Power Law**：改成 ELECTRL（或更具体的 MDEA/ACIDS/AMINES）
4. **如果电离反应被错写为 Power Law**：改成 INST-EQ / INSTANT
5. **跑 Rate-Based 看 Profile E 列**：电离应该不显示 E 值（瞬时）；限速反应应该 E > 1
6. **如果有 E = 1 的限速反应出现**：回去查 Reaction type 是否漏改

---

## 6. Rate-Based 5 步操作

> 从 Equilibrium 平衡级 RadFrac 切换到 Rate-Based（RateSep/RateFrac）的 MDEA 反应吸收塔，需要重新选 **反应类型**、**复核 Bulk/Film Reactions 配置**。本步骤给出完整操作 SOP。

### 概览：两层修改

"重新选定速率增强因子模板"在 Aspen Plus 里**不是一个按钮**——分布在两个地方共同实现：

| 层面 | 路径 | 作用 |
|------|------|------|
| **L1 反应集** | Setup → Reactions → RMDEA → Kinetics 表 | 告诉 Aspen "这是电解质反应"，按反应类调内部默认算法、k、K_eq、增强因子 |
| **L2 塔块配置** | BlockOptions → B3(RadFrac) → Reactions → **Film Reactions** 子页 / **Bulk Reactions** 子页 | 在 Rate-Based 模式下，按塔板位置复核 Aspen 自动选定的反应处理方式（瞬时 / 速率控制 / Hatta 增强 / Disregard） |

---

### 步骤 1：物性方法前置（必做）

Rate-Based + 电解质**必须有** ELECNRTL 或 ENRTL-RK 之一。

- **ELECNRTL**：传统版，基于 Bunsines-Pitzer-Debye-Hückel + NRTL
- **ENRTL-RK**：改良版（AspenTech 2015+），对 MDEA / MEA-CO₂-H₂O 系统有专门回归参数
- **v12 之后**：建议默认 ENRTL-RK（除非有历史数据对比证明 ELECNRTL 更优）

数据库：AQUEOUS 必勾（电离、电解质默认参数都来自这里）。

---

### 步骤 2：反应集（Reactions | RMDEA）反应类型重选

打开 RMDEA 的 Kinetics 子表，对每个反应设 Reaction type：

| Rxn | Reaction type 设置（必须改 Power Law 默认）| 备注 |
|-----|--------------------------------------------|------|
| R2-R6 | `INST-EQ` 或 `INSTANT` | 电离瞬时，不进 KINETIC |
| **R7**、R8 | **`ELECTRL`** 或 **`ACIDS`** 通用电解质 | Aspen 会用 k = 4.32e13 / E = 13.249 kcal/mol 内置值 |
| **R11**、R12 | **`MDEA`** 或 **`ACIDS`** 或 **`AMINES`** | 推荐 `MDEA`——专用模板，调用叔胺 CO₂ 水合机理内置 k |

> **关键**：打开 R11 Kinetics 表后，看 Reaction type 列下拉菜单。本步是 Rate-Based 操作的核心。

可选：覆盖默认 k、Ea（如果项目有特殊值或实验室回归），但**头一次先保留内置默认**验证模型能收敛。

---

### 步骤 3：切 RadFrac 到 Rate-Based

1. 流程图上点 B3
2. Configuration 标签 → Calculation type：
   - Equilibrium → **Rate-Based**
3. 新出现的子标签：
   - **Convergence** 页：默认 abort 即可
   - **Rate-Based / EO Modeling**：配 Bulk/Film 离散数（默认 5/5）、传质关联式（默认 `Default`）、Area 关联式（默认 `Default`）
4. 左导航树 `B3 | EO Modeling` 子树自动出现：
   - Bulk → Reactions
   - Film → Reactions
5. 反应集不需要重新关联——RMDEA 自动绑定。

---

### 步骤 4：复核 Bulk Reactions（液相体相反应）

路径：`B3 → EO Modeling → Bulk → Reactions`

- **R2-R6**：应自动为 `Disregard` 或 `Instantaneous`（在 Bulk 里按瞬时算）
- **R7、R8、R11、R12**：必须为 `Rate-controlled`（含增强因子 E）
- 如果出现 `Disregard` → **手改 `Rate-controlled`**

> **关键差异**（vs 平衡级）：
> - 平衡级：反应只在体相里按反应方程算
> - Rate-Based：反应**同时在液膜内 + 体相内**，液膜内受 Hatta 增强因子修正

---

### 步骤 5：复核 Film Reactions（液膜反应）

路径：`B3 → EO Modeling → Film → Reactions`

Aspen 根据 RSet 的 Reaction type 字段自动设定 Film 处理方式：

| Rxn（Reaction type）| 期望的 Film 处理 | 期望 E 值 |
|--------------------|----------------|----------|
| R2-R6（INST-EQ / INSTANT）| Instantaneous | 不显示 E（已瞬时）|
| **R7**（ELECTRL/ACIDS）| Rate-controlled + Hatta | **E ≈ 1.5-5** |
| **R8**（ELECTRL/ACIDS）| Rate-controlled + Hatta | E ≈ 1.5-5 |
| **R11**（MDEA/ACIDS/AMINES）| Rate-controlled + Hatta | **E ≈ 3-15（核心）** |
| R12（反向反应）| Rate-controlled + Hatta | E ≈ 3-15 |

**关键检查项**：

- 如果 R7/R8/R11/R12 的 **E = 1.0**：说明 Aspen 没启用增强因子，是错的！
  - 回去步骤 2，把 Reaction type 改成 ELECTRL / ACIDS / AMINES / MDEA
  - 重跑初始化 + Run
- 如果 Film 处理显示为 `Disregard`：手改为 `Rate-controlled with Hatta enhancement`

---

### 反应类型选择速查表（Step 2 选什么）

| 工艺 | 推荐的 Reaction type |
|------|--------------------|
| MDEA（仲胺催化 CO₂ 水合）| `MDEA` / `ACIDS` / `AMINES` |
| MEA（伯胺 + zwitterion）| `AMINES` / `ACIDS` |
| DEA（二乙醇胺）| `AMINES` / `ACIDS` |
| K₂CO₃（热钾碱）| `ELECTRL` / `K2CO3` |
| NaOH（强碱脱碳）| `ELECTRL` |
| Hot Potassium Carbonate（Benfield）| `ELECTRL` / `K2CO3` |
| 通用电解质（无现成模板）| `ELECTRL` |

> **`ELECTRL` 是保底选项**——任何电解质体系都不会错，但通常不能精确调用某个胺类的内部专属 k 数据。
> `MDEA`、`AMINES`、`ACIDS` 是更精确的——但需要 Aspen 模板支持（≥ v11 都有）。

---

### 增强因子算法的可选替代

Aspen 默认用 **Hatta 法**。在 Film Reactions 子页，`Enhancement algorithm` 可以改：

| 算法 | 适用 |
|------|------|
| `Hatta`（默认）| 假一级（CO₂ + 胺）或慢反应（k·C_胺 >> k_L·a）|
| `General Enhancement` | 二级反应（k_OH⁻·C_OH⁻ 量级）|
| `Three-Film` | 多组分扩散耦合 |
| `User Kinetics` | 用户 Fortran 子程序 |

MDEA 体系**常规用 `Hatta` + 内置 k** 是工业默认做法。

---

### 典型操作流程的完整时间估算

| 步骤 | 时间 | 备注 |
|------|------|------|
| 改 Reaction type（11 反应）| 5 min | 每个反应 30 秒 |
| 切 RadFrac 到 Rate-Based + 配置参数 | 10 min | Bulk/Film 默认值 |
| 复核 Bulk/Film 配置 | 15 min | 检查 8-10 项 |
| 第一次 Run（可能卡）| 1-3 min / 板 | Rate-Based 比平衡级慢 5-20 倍 |
| 校核 Profile | 30 min | 与中试数据对比 CO₂ 脱除率 |

总计一次完整 Rate-Based 切换：约 1.5-3 小时（MDEA 体系 12-20 板）。

---

### 必查关键指标（跑完后）

| 指标 | 期望值范围 | 红线 |
|------|----------|------|
| Profile | E（增强因子）| **3-15**（塔内 CO₂ 段） | E=1 即错 |
| Profile | 塔内液膜厚度 | 0.1-1 mm | 异常厚/薄即不平衡 |
| Profile | 塔内液体流率 | 与设计符合 ±10% | 大偏差即计算发散 |
| CO₂ 脱除率 | 与中试 ±5% | 偏差 >15% 即警告 |
| 物料平衡 | 进 = 出 ±0.5% | 偏差 >1% 警告 |

---

### 常见失败模式与处置

**失败 1：模型不收敛 + 报 "stiff ODE"**

- 原因：R2-R6 被错设成 KINETIC
- 处置：改成 INST-EQ，重跑

**失败 2：CO₂ 脱除率异常偏低（<70%）**

- 原因：E=1（增强因子未启用），Reaction type 还是 Power Law
- 处置：R7/R8/R11/R12 改成 ELECTRL/ACIDS/MDEA

**失败 3：CO₂ 脱除率异常偏高（>99.9%，远高于实验）**

- 原因：R7/R8 在高 OH⁻ 区反应过量；或 Reaction type 用错（MDEA vs MEA）
- 处置：核对 Reaction type + 反应级数

**失败 4：跑通但物料不平衡 >1%**

- 原因：反应集里 R7/R8 的 K_eq 与 R11/R12 的 K_eq 不自洽
- 处置：换 AspenTech 官方模板的反应集；不要自己随便改 K_eq

**失败 5：跑出来 CO₂ 脱除率与中试差 >20%**

- 多数情况是**n=0 问题**（Reaction Set 把 R11/R12 的 n 错设成 0）
- 处置：把 n 改回 1

---

### 模板与脚本

AspenTech 在以下位置提供官方 Rate-Based MDEA 模板：

```
Aspen Plus 安装目录\Engine\Examples\Rate-Based\CO2-Capture\
   ├── CO2Capture-DEA.apw       (DEA 模板)
   ├── CO2Capture-MDEA.apw      (MDEA 模板)
   ├── CO2Capture-MEA.apw       (MEA 模板)
   └── CO2Capture-NaOH.apw      (NaOH 原始模板)
```

打开任一文件，对照 Reaction type、Bulk/Film Reactions 配置——可直接 fork 到女王的项目里。

---

## 7. 动力学参数溯源

> Aspen 默认反应集里，CO₂ + OH⁻、CO₂ + 胺这类反应的 k、Ea 数值**不是占位符**——有明确出处。本章给出完整溯源链 + 单位反算演示，供项目审计 / 合规审查 / 学术报告引用。

### 完整溯源链

```
Pinsent (1956) 实验测定了 CO₂ + OH⁻ 的 k、Ea
        ↓ 多名学者多温度区间重新回归
Hikita 1976 / Pohorecki-Monuik 1988 / Austgen 1989（AIChE J. 35:1754）/
Sada 1987 / Danckwerts 等多组参数
        ↓ Aspen Tech 集成到 Rate-Based 模板
AspenTech (2008) "Rate-Based Model of CO₂ Capture Process by NaOH"
   R7: CO₂ + OH⁻ → HCO₃⁻
   k = 4.32 × 10¹³ m³/(kmol·s)，E = 13.249 kcal/mol
        ↓ 派生出多套官方模板
   K₂CO₃ 模板（2010）、Hot Potassium Carbonate 模板、MDEA Rate-Based 模板、
   MEA Rate-Based 模板、PZ/AMP 模板均沿用同一组（反应 7）
        ↓ 被引用到工程文献
3rd-party 模拟（Chalmers/DiVA/Polimi/Mourad 等）→ 均沿用该默认值
```

### 出处 1：Pinsent 1956（Pinsent, Pearson & Roughton）

> **原始文献**：
> Pinsent, B.R.W., Pearson, L., Roughton, F.J.W. (1956)
> "The kinetics of combination of carbon dioxide with hydroxide ions"
> *Trans. Faraday Soc.* **52**: 1512-1520

**关键结论**：

- 反应：CO₂ + OH⁻ → HCO₃⁻
- 实验方法：温度跳跃（temperature-jump）松弛法
- 活化能 Ea ≈ 13 kcal/mol（与"13.249"一致）
- 速率常数（关联式）：log₁₀k = 8.916 - 1325/T [L/(mol·s)]

注意：Pinsent 同一篇论文里**同时测定了多对碳酸氢盐反应**：

- CO₂ + H₂O ⇌ H₂CO₃（不同 Ea）
- CO₂ + OH⁻ ⇌ HCO₃⁻（本题关注）
- HCO₃⁻ 解离（HCO₃⁻ ⇌ H⁺ + CO₃²⁻）

**Aspen 框里常见的 "13.249 kcal/mol"** 直接来自 Pinsent 论文里 CO₂ + OH⁻ 那条反应——是 Aspen 重编码后的值。

### 出处 2：Hikita 1976

> **原始文献**：
> Hikita, H., Asai, S., Himukashi, Y., Inoue, T., Kobayashi, T. (1976)
> "Absorption of carbon dioxide into aqueous sodium hydroxide and potassium hydroxide solutions"
> *Kagaku Kogaku Ronbunshu* **2**: 233-238

**关键结论**：

- 反应：CO₂ + NaOH / KOH 液相吸收
- 给出的 k_OH⁻ 比 Pinsent 高约 50%（因为是在高浓度强碱条件下测的）
- 关联式：k_OH⁻ = 9.77 × 10¹⁰ m³/(kmol·s), E = 41.2564 kJ/mol
- 这是 Polimi 文献（2017/2019）引用的版本

### 出处 3：Austgen 1989

> **原始文献**：
> Austgen, D.M., Rochelle, G.T., Peng, X., Chen, C.C. (1989)
> "Model of Vapor-Liquid Equilibria for Aqueous Acid Gas-Alkanolamine Systems"
> *AIChE Journal* **35**(11): 1754-1765

**关键贡献**：

- 在 Pinnent / Hikita 数据基础上**重新拟合**，专门针对 MEA / DEA / DGA / MDEA 体系
- 与电解质 NRTL 模型匹配
- AspenTech 的 Rate-Based MDEA 模板沿用了这一拟合思路

### 出处 4：AspenTech 2008 官方模板

> **原始文档**：
> Aspen Technology, Inc. (2008)
> "Rate-Based Model of the CO₂ Capture Process by NaOH"
> 文档内嵌在 Aspen Plus 安装示例中

**关键数据（沿用至今）**：

| 反应 | k | E |
|------|---|---|
| CO₂ + OH⁻ → HCO₃⁻ | 4.32 × 10¹³ m³/(kmol·s) | 13.249 kcal/mol |
| HCO₃⁻ → CO₂ + OH⁻ | 2.38 × 10¹⁷ | 29.451 kcal/mol |
| 2 H₂O ⇌ H₃O⁺ + OH⁻ | 1.04 × 10¹⁶ | 25.487 kcal/mol （瞬时电离）|
| 2 H₂O + CO₂ ⇌ HCO₃⁻ + H₃O⁺ | 4.32 × 10¹³ m³/(kmol·s) | 13.249 kcal/mol |
| Ca(OH)₂ ⇌ CaOH⁺ + OH⁻ | （瞬时）| — |
| CaCO₃(固) ⇌ Ca²⁺ + CO₃²⁻ | （盐沉淀）| — |
| NaOH → Na⁺ + OH⁻ | （解离）| — |
| Na₂CO₃ → 2Na⁺ + CO₃²⁻ | （解离）| — |
| NaHCO₃ → Na⁺ + HCO₃⁻ | （解离）| — |

**第三方引用证明**：

| 来源 | 引用数据 | 引用说明 |
|------|---------|---------|
| Mourad et al. 2022（PMC9178620）| k=4.32×10¹³, E=55470.9 J/mol | "Some of the values are obtained from the literature as well as from Aspen itself." |
| DiVA 论文 (2023) | R(38): k=4.32E+13, E=13249 cal/mol | 明确注 "sourced from Aspen Technology 2008 (Rate-Based model of the CO2 capture process by NaOH)" |
| Polimi 论文 (2017) | k_OH⁻ = 9.77×10¹⁰ m³/(kmol·s), E = 41.2564 kJ/mol | "from Hikita et al. for Eq.(12)" —— 注 Polimi 给的是 Hikita 拟合，但数量级一致 |
| Chalmers 硕士论文 (aMDEA) | R6: k=4.23e13, E=5.547e7 J/kmol | 与 Aspen 模板数同源（仅系数略有简化）|

### 单位换算演示（4.32e13 → 7.9 L/(mol·s)）

**问题**：框里写 `k = 4.32 × 10¹³`，是否合理？

**关键步骤**：理解 Aspen POWERLAW 在 `[Cᵢ] basis = Molarity` + `Rate basis = Reactor volume` 时的 k 单位。

#### 单位换算的逻辑

Aspen Power Law 默认表达式：

- rate = k · exp(-E/RT)
- 当 n=0, rate 单位 = [mol/(L·s)] 或 [kmol/(m³·s)]（取决于 reactor volume basis）

所以 k 的等效单位：

- n=0 + Reactor volume basis：**k 单位 = m³/(kmol·s)** （**不是 L/(mol·s)**）

但很多人**直接把 4.32e13 当成 L/(mol·s) 看作"9 个数量级大"** —— 这是错误的。

#### 反算演示

已知：

- k = 4.32 × 10¹³ m³/(kmol·s)
- E = 13.249 kcal/mol = 55470.9 J/mol
- T₀ = 298.15 K

计算：

$$k(T) = k_0 \cdot \exp\!\bigg(-\frac{E}{RT}\bigg)$$

$$k(298.15) = 4.32 \times 10^{13} \cdot \exp\!\bigg(-\frac{55470.9}{8.314 \times 298.15}\bigg)$$

$$= 4.32 \times 10^{13} \cdot e^{-22.376}$$

$$= 4.32 \times 10^{13} \times 1.83 \times 10^{-10}$$

$$= 7.92 \times 10^{3} \;\text{m}^3\!/\!(\text{kmol·s})$$

$$= 7.92\;\text{L/(mol·s)} \quad \checkmark$$

#### 与文献对比

| 来源 | k(298) 单位 L/(mol·s) | 备注 |
|------|---------------------|------|
| **Pinsent 1956 (Trans. Faraday Soc.)** | log₁₀k = 8.916 - 1325/298 ≈ **10^4.47 ≈ 2.95 × 10⁴** | 实验测定的上限 |
| **Hikita 1976** | ≈ 5.7 × 10³ | 高浓度强碱下 |
| **AspenTech 2008 模板**（女王截图）| **7.92 × 10³** | 拟合后 |

差异 1.4-3.7 倍，**同一数量级**——Aspen 框里"4.32e13"是合理的工程值。

### 单位混淆典型错误

#### 错误 1：把 k 当成 L/(mol·s)

- **症状**：看到 4.32e13 当 L/(mol·s) 用 → 比文献大 10⁹ 倍 → 以为输错了
- **正确做法**：反算到 298 K 的等效 L/(mol·s) 值（7.92），与文献 5.7 × 10³ - 2.95 × 10⁴ 对比 → 在同一数量级

#### 错误 2：把 E 当成 J/mol

- **症状**：看到 13.249 当 J/mol → 与 J/mol 量级的文献数据（55000、60000 J/mol）对比 → 小 1000 倍 → 以为输错了
- **正确做法**：看 Aspen 框里的实际 E 单位（默认 **cal/mol**），换算系数 1 cal/mol = 4.184 J/mol
- 13.249 cal/mol × 4.184 = **55.47 kJ/mol**——与 Pinsent 一致

#### 错误 3：把 k 的单位改成 SI 后没换算数值

- **症状**：项目交付时改 Aspen 全局 ENG units 为 SI，框里 k 显示成 1.81e10（其实是 kJ/mol 与 cal/mol 的 1/4.184 转换）
- **正确做法**：换 ENG units 后，Aspen 自动重算；但如果硬填文本，要重新按 kcal → kJ、m³/(kmol·s) → m³/(kmol·s)（不变）校准

#### 错误 4：把 T₀ 留空后忘记阿伦尼乌斯 T 参考

- **症状**：对比多个数据源，发现同一 E 但 k 差很多
- **正确做法**：对照两个源都使用**相同的 T 参考**。如果源 1 用 T₀ = 298.15 K、源 2 用 T₀ 未指定（默认 0 K），k 数值绝对不同（外推到 T→∞ 与 T=298 不同含义）

### 关联研究与工业"非默认"k 数据

#### Hikita / Sada / Crittenden 等日本/英国学派（1960s-1980s）

- **Hikita 1976**：CO₂ + NaOH/KOH 吸收，9.77 × 10¹⁰ m³/(kmol·s), E = 41.26 kJ/mol
- **Sada 1987**：CO₂ + 各种氨基酸盐，回归到与 Hatta 法一致
- **Crittenden 1988**：CO₂ + 醇胺，多组分回归

#### 现代文献（2009-2024）

- **Puxty et al. 2009**（*Environ. Sci. Technol.* 44: 457-462）：CO₂ + 33 种胺的速率筛选
- **Kim et al. 2009**（*J. Chem. Eng. Data*）：CO₂ + PZ 在高温下测量
- **Mourad et al. 2022**（PMC9178620）：K₂CO₃-glycine 混合体系
- **Zhang et al. 2023**（*Sep. Purif. Technol.*）：新一代 MDEA + PZ 混合吸收剂

**Aspen 默认值往往比新文献保守 1.5-3 倍**——这是有意为之（确保 Aspen 模型偏向安全侧）。

如果项目需要更新 k 值（实验室新测 / 文献新发表）：

1. 在 Kinetics 表里覆盖 E 与 k（保留 T₀ = 298.15 K 写法）
2. 同时更新 K_eq（K_eq = k_forward / k_reverse 在 Aspen 自动算）
3. 在 Project Notes 注明来源（合规审计要求）

### 项目报告与论文的标准引用格式

#### 模板（ASPEN 默认）

```
Aqueous electrolyte reaction kinetics for CO₂ + OH⁻ are based on the
Rate-Based Model of the CO₂ Capture Process by NaOH (Aspen Technology, Inc., 2008),
which uses kinetic parameters from Pinsent, Pearson, Roughton (1956) and Hikita et al. (1976).
CO₂ + OH⁻ → HCO₃⁻ : k = 4.32 × 10¹³ m³/(kmol·s), E = 13.249 kcal/mol
```

#### 模板（自定义）

```
Rate constants for CO₂ + MDEA + H₂O reaction were obtained from
[文献源], re-fitted to the Arrhenius expression [具体形式].
Reaction 11 (MDEA catalytic CO₂ hydration):
   k = [A] m³/(kmol·s), E = [Ea] kcal/mol
Reference: [完整引用]
```

### 操作建议（最后说一遍）

当女王下次拿到反应集 Aspen 文件，按下面顺序审计：

1. **看每个反应的 Reaction type**：必不是 Power Law 默认
2. **看 k、Ea 是否在合理范围**（反算到 298 K 的 L/(mol·s) 量级 1-100）
3. **看 n**：CO₂ 反应对 CO₂ 必须 n ≥ 1（n=0 即红旗）
4. **核对数据来源**：每个 k 都必须能溯源到具体文献
5. **项目记录保留 Aspen 默认值出处**（AspenTech 2008 模板 + Pinsent 1956 + Hikita 1976）

如果任何一个对不上，回本参考文档重新审视。

---

## 8. 联动规则与失败模式

### 联动规则

| 联动对象 | 时机 |
|---------|------|
| 母 SKILL `petrochem-process-design` | 工艺专业语境（设备/物料/反应选择）|
| `pid-pfd-v69-standards` | 出胺液 P&ID/PFD 时联动（18 铁律）|
| `process-sim-column-analysis` | 走 Aspen Custom Modeler / Fortran 子程序 / HYSYS 对比时联动 |

### 失败模式与陷阱

| 症状 | 原因 | 处理 |
|------|------|------|
| 不收敛（RadFrac Rate-Based 跑不通）| 反应 2-6 用了 Power Law / KINETIC | 改回 INST-EQ |
| CO₂ 脱除率异常偏低 | Rate-Based 模式下 E = 1（增强因子未启用）| 回 Reaction type 改 ELECTRL/ACIDS/MDEA |
| 模型与中试 CO₂ 脱除率偏差 >15% | k、Ea 单位换算错了 / n 不对 | 复位 n = 1、Ea 文献值 |
| 缺反应 9、10（跳号）| 反应集曾经编辑过又删除的残留 | 不影响模拟；如要清洁化重编 |
| 项目审计被退回 | k、Ea、n 数据未注明来源 | 用第 7 章溯源到 AspenTech 2008 文档 |

### 版本

- v1.0.0（2026-08-07）：基于女王这一轮对话形成的初始版本
  - 来源：女王 Aspen 截图 + web 文档核验（PMC9178620 / DiVA / Polimi / Chalmers）
  - 涵盖：MDEA / DEA / MEA / K₂CO₃ / Hot Potassium Carbonate 体系共享的标准 11 反应
- 后续迭代触发：
  - 女王提供新截图/新工艺包（DEA、MEA）→ 扩本文件第 4 章
  - 发现新的溯源文献（如 Sada 1987、Kim 2009 复测数据）→ patch 第 7 章
  - 新版 Aspen Plus 菜单路径变 → patch 第 6 章

---

> **关联位置**：本文件位于
> `~/.hermes/skills/engineering/petrochem-process-design/references/aspen-amine-simulation-comprehensive.md`
>
> 母 SKILL：`petrochem-process-design/SKILL.md` 的 references 目录内。