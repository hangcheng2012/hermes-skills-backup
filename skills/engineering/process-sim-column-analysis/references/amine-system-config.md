# 胺液脱酸气塔标准配置

女王 07-18 实战：胺液再生塔在 Aspen Plus 和 HYSYS 中的标准配置，含反应框架、物性方法、动力学选择。

## 一、核心区分：HYSYS vs Aspen Plus 的胺液能力

| 软件 | 胺液动力学 | 说明 |
|------|-----------|------|
| **Aspen HYSYS + Acid Gas 模块** | ✅ 内置 | MEA/DEA/MDEA/PZ 等胺液动力学内置（需单独购买 Acid Gas Cleaning 许可证）|
| **Aspen Plus** | ❌ 需手输 | 不带胺液动力学，必须手动输入反应（含 LHHW 速率表达式）|

**女王 07-18 T-101 用的是 HYSYS 的 Acid Gas - Chemical Solvents**，确认 HYSYS 端有内置胺液动力学。

## 二、HYSYS Acid Gas 模块（女王当前使用）

### 模块支持范围

HYSYS Acid Gas - Chemical Solvents 物性包支持：
- MEA（乙醇胺）
- DEA（二乙醇胺）
- MDEA（甲基二乙醇胺）
- DGA（乙二醇胺）
- TEA（三乙醇胺）
- DIPA（二异丙醇胺）
- PZ（哌嗪）
- 任意两种胺的混合配方
- Sulfolane + MDEA / DIPA（砜胺法）
- MDEA + MEA + DEA 混合

### 标准塔配置（胺液脱酸气）

**典型流程**：
1. 进料气（含 CO₂/H₂S）→ Absorber（吸收塔）
2. Absorber 顶部 → 净化气（Sweet Gas）
3. Absorber 底部 → 富液（Rich Amine）
4. 富液 → 闪蒸罐 → 分离烃类
5. 富液 → Lean/Rich 换热器（与贫液换热）
6. 富液 → Regenerator / Stripper（再生塔）
7. Regenerator 底部 → 贫液（Lean Amine）
8. 贫液 → 泵 → 冷却器 → 循环回 Absorber

**再生塔通常配置**：
- 类型：**Reboiled Absorber**（顶部无冷凝器，有再沸器）
- 塔板数：8-20 块（实际工业值）
- 进料位置：中上部
- 顶部压力：约 30 kPag（微正压）
- 底部温度：110-125°C（取决于胺种类和压力）
- 回流比：**很低（0.1-0.5）或无外回流**

### HYSYS 操作关键点

1. **选 Fluid Package**：Acid Gas - Chemical Solvents
2. **添加组分**：H₂O + 胺（MDEA 等）+ CO₂ + H₂S + 进料中其他组分
3. **进 Absorber 模板**：
   - 类型：Absorber
   - 添加 Reactions（自动启用 Acid Gas 动力学）
4. **进 Regenerator 模板**：
   - 类型：Reboiled Absorber（**不是 Distillation**）
   - 关联 Absorber 的 Reactions
5. **冷凝器**：
   - 顶部通常**无冷凝器**（Reboiled Absorber 类型）
   - 如出现"顶部 25°C 黄高亮" → 检查塔类型是否正确
6. **回流比**：
   - 胺液再生塔回流比应很低（0.1-0.5）
   - 看到 12.48 这种高值 → 检查塔类型或 Reflux 字段是否填错

### HYSYS 调收敛

- **Parameters → Solver → Damping Factor**：胺液推荐 0.25-0.5（默认 1.0）
- **迭代次数**：默认够用，但胺液有时需加大
- **初始估计**：Parameters → Profiles 给温度、压力、组分分布填合理值

## 三、Aspen Plus 胺液配置（参考用）

### 物性方法

- **ELECNRTL**（Electrolyte NRTL）：胺液体系**标配**
- ENRTL-RK / ENRTL-HF / ENRTL-HG：变种
- 内置 databank 含 600+ 电解质离子对的二元交互参数

### 反应框架

Aspen Plus **不带胺液动力学**，必须手动设置反应。

#### 步骤 1：用 Electrolytes Wizard

```
Data Browser → Reactions → 选 "Use Electrolytes Wizard"
```

向导生成默认反应集：
- 水的电离：`H₂O ⇌ H₃O⁺ + OH⁻`
- 胺的电离：`MDEA + H₂O ⇌ MDEAH⁺ + OH⁻`
- CO₂ 溶解：`CO₂ + 2H₂O ⇌ H₃O⁺ + HCO₃⁻`
- 氨基甲酸酯（仅 MEA/DEA）：`MEA + CO₂ + H₂O ⇌ MEACOO⁻ + H₃O⁺`
- H₂S 溶解：`H₂S + H₂O ⇌ H₃O⁺ + HS⁻`

**重要提示**：向导生成的是**默认反应集**，用户必须根据工艺条件增删。

#### 步骤 2：选建模方法

| 方法 | 含义 | 推荐场景 |
|------|------|---------|
| **True Component Approach** | 直接跟踪离子 | ⭐ 严格模拟，推荐 |
| Apparent Component Approach | 把离子"藏"在分子组分里 | 老旧方法，仅做简化对比 |

#### 步骤 3：动力学（必须手输）

Aspen Plus 不带胺液动力学，常见做法：

**方案 A：EQUILIBRIUM（平衡模型）**
```
Reactions → New → Type: EQUILIBRIUM
输入 Keq 关联式（来自文献）
```
工业常用，适合工艺设计初算。

**方案 B：LHHW 动力学（严格速率模型）**
```
Reactions → New → Type: LHHW
输入：
- 指前因子 A
- 活化能 E
- 吸附参数
```

**常见胺液动力学参数来源（文献）：**

| 体系 | 来源 |
|------|------|
| MEA + CO₂ | Hikita et al. (1977), Pinsent et al. (1956) |
| MDEA + CO₂ | Ko & Li (1990), Versteeg et al. (1996) |
| MDEA + H₂S | Yih & Shen (1988) |
| DEA + CO₂ | Hikita et al. (1977) |
| AMP + CO₂ | Alper (1990) |

### Aspen Plus 塔模型选择

| 模型 | 用途 |
|------|------|
| **RadFrac (Equilibrium)** | 工业初算，标准精馏算法 |
| **RadFrac (Rate-Based)** ⭐ | 严格模拟，含传质阻力 |
| **RateSep** | 替代 Rate-Based RadFrac 的独立模块 |

**推荐**：工业胺液再生塔设计用 **RadFrac Rate-Based + LHHW 动力学**。

## 四、关键提示

### 1. HYSYS Acid Gas 模块 ≠ Aspen Plus 内置

容易混淆：
- **Aspen HYSYS Acid Gas Cleaning**（带动力学，需购买）= 女王 07-18 用的
- **Aspen Plus 默认安装** = **不带**胺液动力学，必须手输

### 2. 不用向导手写反应也可以，但要遵守：

- 电中性约束（Charge Balance）
- 离子对的 chemical species 命名规范
- 反应 ID 以字母开头，限长（Aspen Plus 有字符限制）

### 3. 两种软件工业实测对比

| 维度 | HYSYS Acid Gas | Aspen Plus + 手输 |
|------|---------------|-------------------|
| 设置难度 | 简单（向导式） | 复杂（需懂热力学 + 动力学） |
| 灵活性 | 中（受内置包限制） | 高（完全自定义） |
| 精度 | 工业可用 | 学术 / 严格设计首选 |
| 适用场景 | 工厂日常工艺模拟 | 设计院、科研、特殊配方 |

### 4. 女王常用工作流

**工厂项目**：HYSYS Acid Gas → 30 分钟跑通 → 出报告
**设计院项目**：Aspen Plus ELECNRTL + LHHW → 严谨动力学 → 出设计文件
**特殊配方 / 新胺液**：Aspen Plus → 完全自定义 → 文献查参数

### HYSYSAcid Gas 模块的 Efficiency vs Advanced Modeling（女王 09-01 关键发现）

**AspenTech 官方 Jump Start Guide（AT-03943-0318, 2018）原文**：

> "The 'Efficiency' option is the one most commonly used; it is a highly rigorous method that uses rate-based calculations in the background to calculate stage efficiencies of H2S and CO2, and then uses these values to solve the column."

Acid Gas 包内部有两种建模选项：

| 选项 | 工作机制 | 速度 | 精度 | 适用场景 |
|---|---|---|---|---|
| **Efficiency**（默认） | 内部 rate-based 算 H2S/CO2 的 component efficiency → 用算出的 efficiency 求解整塔 | 快 | 工业级 | **工艺设计、塔盘水力学、vendor 出图（推荐）** |
| **Advanced Modeling** | 全塔 rate-based（每块板按双膜理论算传质 + 反应） | 慢 | 研究级 | 反标工厂数据、研究验证

**核心：Acid Gas 包默认用 Component 模式（不是 Overall 模式）**

- **改 Overall 效率对 H2S/CO2 component efficiency 无影响**（cheresources 论坛 Ceng 2013 年困惑的根因）
- Acid Gas 包内部直接用 rate-based 算 H2S/CO2 的 component efficiency，绕过 Overall 字段
- 所以 **Overall 全塔效率 0.3-0.45 在 Acid Gas 胺液塔里不适用**——必须按组分查 H2S/CO2 的 component efficiency

**等效理论板换算（女王 09-01 命题）**：

> N_理论_H2S = N_实际 × η_H2S
>
> N_理论_CO2 = N_实际 × η_CO2

**条件**：所有板上 η 一致时简化成立（女王 T-100 截图：H2S 在 7 块板上都是 0.750）。不同板 η 不同时不能直接乘，要 HYSYS 内部逐板算或按对数平均。

### H₂S 实际工程 component efficiency 典型值

| 来源 | η_H2S | η_CO2 | 说明 |
|---|---|---|---|
| **HYSYS Acid Gas 自动算出** | 0.4-0.8（取决于工况） | 0.05-0.25 | T-100 截图：H2S=0.75, CO2=0.15 |
| Mahdipoor 2024 论文（AGE 塔） | 4.1% | 21.4% | 极端工况，极低效率 |
| Aspen Plus 典型范围 | 0.5-0.8 | 0.1-0.3 | 工业设计参考 |
| 经验值（cheresources Dacs 2009） | 0.30-0.45 Overall | — | **整塔加权，Acid Gas 塔不适用** |

### Overall 模式 vs Component 模式（清晰对照）

| 模式 | 效率设值 | 适用场景 | Acid Gas 包是否用？ |
|---|---|---|---|
| **Overall**（全塔统一） | 一个效率值（如 0.35），所有组分、所有板共用 | 简单精馏塔 | **否**（被绕过） |
| **Component**（按组分）⭐ | 每个组分在不同板上效率独立 | **化学吸收塔（Acid Gas 胺液塔）** | **是（默认）** |

**为什么 amine 塔必须用 Component 模式**：H2S 在 MDEA 中是质子瞬时反应（效率高，0.5-0.8），CO2 在 MDEA 中是慢反应（效率低，0.1-0.3）—— 用 Overall 一个数（如 0.35）物理上不准确。Component 模式反映这个本质差异。

---

## 五、Number of Stages 字段的核心坑（Murphree 输入模式切换）

### 核心结论（女王 09-01 明确要求固化）

**理论板数 ≠ 实际板数，即使填了 Murphree efficiency，两者也不相等。**

HYSYS 的 "Number of Stages" 字段在两种模式下含义不同：

| 模式 | Number of Stages 含义 | Murphree 字段 |
|---|---|---|
| **不填 Murphree**（默认 100%） | **理论板数**（每块板都是理想平衡级） | 默认 100%，可不动 |
| **填了 Murphree efficiency** | **实际物理板数**（HYSYS 用 Murphree 公式修正每块板的平衡） | 按现场效率填 |

**换算关系（最朴素写法）**：

> N_理论 = N_实际 × η

> N_实际 = N_理论 ÷ η

其中 η 是单板效率（Murphree）。

**举例**：胺法脱 H₂S 吸收塔，板效率 30%，实际板 30 块 → 理论板 = 30 × 0.30 = 9 块。

### 两种做法的对比

| 做法 | Number of Stages | Murphree | 适用场景 |
|---|---|---|---|
| **做法 A**（推荐设计用） | 填理论板数 | 不填（默认 100%） | 工艺设计、塔盘水力学、vendor 出图 |
| **做法 B** | 填实际板数 | 填现场效率 | 反标工厂实际数据、现场标定 |

### 关键陷阱：塔盘水力学必须用理论板

工业论坛老专家（50 年经验的 Bobby Strain、HYSYS 高手 colt16）的一致意见：

> 塔板水力学计算（vendor 做塔盘设计用的 loadings），永远用理论板，不能用实际板。

填了 Murphree 后，HYSYS 算出的回流比、热负荷都会比纯理论板方案**偏低**（因为实际板数更多），拿这数给 vendor 会误判塔径。

### H₂S 吸收塔的板效率典型值

| 塔型 | 单板 Murphree 效率典型值 |
|---|---|
| 普通精馏塔（汽-液） | 60-80% |
| **胺法脱硫吸收塔**（化学吸收） | **25-50%** |
| H₂S 化学吸收段（贫液上部） | 10-25%（极低） |
| H₂S 富液段（接近饱和） | 30-50% |

原因：化学吸收有反应阻力 + 传质阻力双重影响，比物理平衡的精馏效率差很多。胺法塔典型 30-50 块实际板，按 30% 效率算下来也就 10-15 块理论板。

### 推荐工作流（女王做模拟时）

1. **按理论板建模**：Number of Stages = 工艺计算的理论板数，Murphree 不填（默认 100%）
2. **收敛后**检查回流比、热负荷、塔顶塔底组成是否合理
3. **如需对标工厂实测数据**，切到做法 B（实际板数 + Murphree）—— Murphree 必须从工厂实测反算
4. **塔盘 vendor 出图永远基于理论板**（做法 A 的结果）

---

## 六、女王 T-101 实战诊断（07-18 实际遇到）

**问题清单：**
1. 顶部温度黄高亮 25.99°C → **未收敛**
2. Reflux Ratio 12.48 → **异常高**（胺液再生塔应 0.1-0.5）
3. 塔内温度跨度仅 6.1°C → **塔内没真正分离**
4. 冷凝器 + 再沸器配置 → 可能是错配成精馏塔而非 Reboiled Absorber

**建议修复顺序：**
1. 改塔类型：Reboiled Absorber（去冷凝器）
2. 改 Reflux Ratio：调到 0.1-0.5 或不设
3. 检查进料：富液组成（CO₂ loading、胺浓度）
4. Reset → Run → 检查所有值无黄高亮
5. 收敛后再看 Profile 表