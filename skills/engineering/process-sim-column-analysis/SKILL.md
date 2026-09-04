---
name: process-sim-column-analysis
description: Navigate Aspen Plus and HYSYS column profile / column analysis UI for petroleum/chemical engineering work. Load when asked about column profile customization, adding properties (density/viscosity) to profiles, interpreting profile symbols (*, yellow highlight), identifying column type (VL vs LL), or version-specific menu paths.
---

# Process Simulation Column Analysis UI Navigation

Class-level skill for navigating column profile / column analysis features in **Aspen Plus** and **Aspen HYSYS**. Covers both VL (vapor-liquid) and LL (liquid-liquid) columns, with focus on industrial use cases: amine regenerators, distillation columns, absorbers, strippers, extractors.

## When to load

Trigger on any of:
- "如何往 column profile 加密度/粘度/某参数"
- "Table Properties / Filter Setup 在哪里"
- "Profile 里的 * 是什么意思" / "黄色高亮代表什么"
- "怎么判断这台塔是气液还是液液"
- "Column Profiles / Worksheet / Plots 这几个页面有什么区别"
- 涉及 Aspen Plus Display Options / Stream Format
- 涉及 HYSYS Performance / Parameters / Design 任一 tab
- 任何版本相关问题（HYSYS V8/V10/V12/V14 或 Aspen Plus V10/V12/V14）

## Core principles

### 1. 验证优先：UI 路径必须 search 后再答

**女王偏好铁律 (07-18 明确纠正)**：当用户问"某个菜单/按钮在哪"，**必须先 web_search 验证**，不凭印象推断。出错代价高 + 女王标准严格 → "重新网上查找资料" 是常见要求。

具体执行：
- 不同 HYSYS 版本 (V8 → V14) 菜单结构差异巨大
- Ribbon 界面 vs 经典菜单 路径完全不同
- 即使记得路径，**每次回答前都用一次 `web_search`** 复核

### 2. 不要假设 Table Properties 在右键菜单

HYSYS Column Profiles 页面里**有三种右键位置**，结果完全不同：

| 右键位置 | 出现的菜单 | 能否加密度 |
|----------|-----------|----------|
| 空白区域（表边缘） | 页面菜单，无 Table Properties | ❌ |
| 表头（列名） | 列管理菜单，可隐藏列 | 部分 |
| **任意数据单元格** ⭐ | ⭐ **Table Properties / Format / Modify** | ✅ |

女王实测卡点：右键空白区域没看到 Table Properties → 解法：改成**右键数据单元格**（如 105.3°C 那一格）。

### 3. 100% 可靠的后备：Spreadsheet Operation

任何 UI 路径失败时，Spreadsheet Operation 是**所有 HYSYS 版本通用**的终极方案。

调用内部变量的语法：
```
ColumnName.Stage[N].VapourPhase.MassDensity      # 气相质量密度
ColumnName.Stage[N].LiquidPhase.MassDensity       # 液相质量密度
ColumnName.Stage[N].VapourPhase.Viscosity         # 气相粘度
ColumnName.Stage[N].LiquidPhase.Viscosity         # 液相粘度
ColumnName.Stage[N].VapourPhase.SurfaceTension    # 表面张力
ColumnName.Stage[N].VapourPhase.ThermalConductivity
ColumnName.Stage[N].Temperature
ColumnName.Stage[N].Pressure
ColumnName.Stage[N].VapourPhase.MassFlow
ColumnName.Stage[N].LiquidPhase.MassFlow
```

特点：
- 100% 跨版本可用
- 不依赖任何 UI 定制
- 可导出到 Excel（Spreadsheet → Export）
- N 替换为塔板号（1 = 顶部，HYSYS 默认从上往下编号）

### 4. UI 符号含义（必读）

| 符号/颜色 | 含义 | 工程意义 |
|----------|------|---------|
| 数字后带 `*` | 初始估计值（用户填的猜测） | 未收敛，不应用于设计 |
| **黄色高亮** | 同 *（不同版本的视觉提示） | 未收敛 |
| **红色字** | 同 *（部分版本） | 未收敛 |
| 蓝色或黑色字 | 求解器收敛结果 | ✅ 可信 |
| 字底色变红 | 用户主动覆盖了求解器结果 | 手动强制值 |

**女王做设计前务必确认**：所有值不带 *、不黄不高亮——才能用做设计依据。

## 常见误区

### 误区 1：Plots 页面 ≠ Column Profiles 页面

HYSYS 里有两个独立的剖面视图：
- **Plots 页**（Performance → Plots）：快速画图用，有 View Graph / View Table 按钮，**右键无法定制**
- **Column Profiles 页**（Performance → Column Profiles）：主数据表，**右键数据格可调出 Table Properties**

女王卡点：在 Plots 页面右键找不到 Table Properties → 因为该页面没有可定制表格。

### 误区 2：Light/Heavy Key ≠ 液液操作

Light Key / Heavy Key 是**精馏专属概念**，不是液液萃取。
- 精馏塔：Light Key = 塔顶最重组分，Heavy Key = 塔底最轻组分
- 液液萃取塔：没有 Light/Heavy Key 概念
- 看到 Light/Heavy Key 在菜单 → 反而说明塔是**气液精馏**，不是液液

### 误区 3：Filter Setup ≠ Table Properties

- **Filter Setup**：只能隐藏/显示"已经存在"的列（顶部 7 个固定字段）
- **Table Properties**：才能**新增**列（密度、粘度等任意内部变量）

### 误区 4：Fluid Package 决定塔类型支持

| Fluid Package | 支持塔型 |
|---------------|---------|
| **Acid Gas - Chemical Solvents** | 仅气液 (VL) |
| **ELECNRTL** | 气液 / 液液 / 三相 |
| **NRTL / UNIQUAC** | 气液 / 液液 |
| **PR / SRK** | 仅气液 |

**女王 07-18 的 T-101**：用的是 Acid Gas - Chemical Solvents → **100% 是气液塔**。

## 女王胺液再生塔常见异常信号

基于 07-18 实际诊断：

1. **冷凝器温度带黄高亮（≈25°C 默认估计）** → 顶部温度未收敛
   - 检查塔类型是否真的需要冷凝器
   - 胺液再生塔通常用 Reboiled Absorber 类型，无外冷凝器
2. **Reflux Ratio 异常高（12.48）** → 典型胺液再生塔回流比 0.1-0.5
   - 可能是配置错塔类型
   - 或 Reflux Ratio 单位/数值误填
3. **塔内温度跨度 < 8°C** → 塔内没真正分开组分
   - 检查进料组成是否接近平衡
4. **黄高亮不消失** → 收敛问题
   - Parameters → Solver 里调 Damping Factor（胺液推荐 0.25-0.5）
   - 加大迭代次数

## 标准工作流（女王用 HYSYS 胺液塔时）

1. 跑收敛 → 看 Converged 状态
2. 进 Performance → Column Profiles → 检查所有值无黄高亮
3. 右键数据格 → Table Properties → Columns → 勾选 Vapour/Liquid Mass Density 等
4. 进 Performance → Plots → Transport Properties → View Graph 出剖面图
5. 必要时用 Spreadsheet Operation 调内部变量导出
6. File → Print / Export PDF（横向，打印 Converged 工况）

## References

- `references/hysys-column-profile-customization.md` — 详细路径，按 HYSYS 版本分列
- `references/aspen-plus-stream-display.md` — 鼠标悬停 tooltip、Display Options
- `references/column-type-identification.md` — VL vs LL vs 三相 判别
- `references/amine-system-config.md` — HYSYS Acid Gas 模块 + Aspen Plus ELECNRTL 标准配置