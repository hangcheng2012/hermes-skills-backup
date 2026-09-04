# 塔类型识别：气液 (VL) vs 液液 (LL) vs 三相

女王 07-18 实战：当 Plots 页看到 Light/Heavy Key 时问"是不是代表液液"——**理解有偏差**。本文档固化如何从 HYSYS UI 判断塔类型。

## 一、核心纠偏

⭐ **Light/Heavy Key 是精馏概念，不是液液萃取概念。**

| 类型 | Light/Heavy Key 有意义？ |
|------|----------------------|
| 气液精馏塔（Distillation） | ✅ 是 |
| 气液吸收塔（Absorber） | ⚠️ 有时（看分离目标）|
| 气液再生塔（Regenerator） | ❌ 无意义 |
| 液液萃取塔（L-L Extractor） | ❌ 完全无意义 |
| 三相精馏 | ✅ 是 |

**Plots 菜单里出现 Light/Heavy Key 选项 ≠ 正在做液液；这反而说明 HYSYS 提供了这个选项供选择**（菜单项在所有塔里都列出，但不一定是激活的剖面）。

## 二、Light Key / Heavy Key 的精确定义

精馏塔中：
- **Light Key（轻关键组分）**：塔顶产品中**最重**的组分，即"应该从塔顶出去但仍勉强留住的组分"
- **Heavy Key（重关键组分）**：塔底产品中**最轻**的组分，即"应该从塔底出去但仍勉强留住的组分"

**示例（苯-甲苯精馏）：**
- 进料：苯 50% + 甲苯 50%
- Light Key = 苯（沸点 80.1°C，从塔顶出）
- Heavy Key = 甲苯（沸点 110.6°C，从塔底出）

如果是苯-甲苯-二甲苯三元精馏：
- Light Key = 甲苯
- Heavy Key = 二甲苯
- 苯是非关键轻组分（直接全从塔顶出）

## 三、判断塔类型的 5 种方法

### 方法 1：直接看塔类型（最快）

1. 回到主流程图（Main Flowsheet）
2. **双击 T-101 塔图标**进入 Design Tab
3. 顶部会显示塔类型：

| 塔类型字样 | 含义 |
|----------|------|
| `Absorber` | 气液吸收 |
| `Refluxed Absorber` | 气液吸收 + 顶部回流 |
| `Reboiled Absorber` | 气液吸收 + 底部再沸器 |
| `Distillation` | 气液精馏 |
| `Three Phase Distillation` | 三相精馏（V + L1 + L2）|
| **`Liquid-Liquid Extractor`** ⭐ | **液液萃取** |
| `Liquid-Liquid Extractor (with Solvent Recovery)` | 液液萃取 + 溶剂回收 |

⭐ 看到 `Liquid-Liquid Extractor` 字样才是真正的液液塔。

### 方法 2：看进料和产品的相态

1. 进入 T-101 子流程图（Column Environment）
2. 点击每个进料流和产品流
3. 看 **Phase** 标签：

| Phase 标签 | 含义 | 塔类型 |
|----------|------|--------|
| `Vapor` | 蒸汽 | 气液 |
| `Liquid` | 单一液相 | 气液 |
| `Mixed` | 气液两相混合进料 | 气液 |
| `Liquid 1` / `Liquid 2` ⭐ | 两个液相 | **液液** |
| `Vapor + Liquid 1 + Liquid 2` | 三相 | 三相 |

### 方法 3：看 Stream 是否有相标签

液液萃取塔里的流股通常带特殊标签：

| 标签 | 含义 |
|------|------|
| `Aqueous` | 水相（液液萃取常用） |
| `Organic` | 有机相（液液萃取常用） |
| `Light Liquid` | 轻液相 |
| `Heavy Liquid` | 重液相 |

气液塔不会出现这些标签。

### 方法 4：看 Fluid Package 类型

**女王 07-18 实战**：T-101 用的 Fluid Package 是 **Acid Gas - Chemical Solvents**，这个物性包**仅支持气液操作**，不支持液液。

| Fluid Package | 支持塔类型 |
|---------------|----------|
| **Acid Gas - Chemical Solvents** | 仅气液 |
| **Acid Gas - Liquid Treating** | 仅气液 |
| **ELECNRTL** | 气液 / 液液 / 三相 |
| **NRTL / UNIQUAC** | 气液 / 液液 |
| **PR / SRK** | 仅气液 |
| **BK10 / GRAYSON / CHAO-SEA** | 仅气液（炼油） |

⭐ **如果 Fluid Package 是 Acid Gas 系列 → 100% 是气液塔。**

### 方法 5：看 Column Tray Ranges 选项

在 Plots 页面右上角：
- 看到 `All` / `Single Tower` / `From/To` → **气液塔**（只有一个塔段）
- 看到多个塔段范围（如 `Extractor` / `Solvent Recovery`） → **液液萃取塔**（通常分两个塔段）

## 四、HYSYS 内部变量的 Phase 命名

调用内部变量时，Phase 参数用：

| 塔类型 | 有效 Phase 名称 |
|--------|---------------|
| 气液 | `VapourPhase`, `LiquidPhase` |
| 液液 | `LightLiquidPhase`, `HeavyLiquidPhase` |
| 三相 | `VapourPhase`, `LiquidPhase1`, `LiquidPhase2`（或 LightLiquid/HeavyLiquid + Vapour）|

**示例**：
```hysys
# 气液塔
T-101.Stage[3].VapourPhase.MassDensity
T-101.Stage[3].LiquidPhase.MassDensity

# 液液塔
T-101.Stage[3].LightLiquidPhase.MassDensity    # 轻相密度
T-101.Stage[3].HeavyLiquidPhase.MassDensity    # 重相密度

# 三相塔
T-101.Stage[3].VapourPhase.MassDensity
T-101.Stage[3].LiquidPhase1.MassDensity        # 或 LightLiquidPhase
T-101.Stage[3].LiquidPhase2.MassDensity        # 或 HeavyLiquidPhase
```

## 五、女王胺液塔常见误判

| 现象 | 正确判断 |
|------|---------|
| Reflux Ratio = 12.48 | 异常高 → 检查塔类型，可能是精馏配置错 |
| 塔顶温度黄高亮 (≈25°C) | 未收敛 → 改 Reboiled Absorber（无冷凝器）|
| 塔内温跨 < 8°C | 没真正分离 → 检查进料组分 |
| Light/Heavy Key 在菜单里 | 正常现象，不证明塔类型 |

## 六、实操建议

### 1. 接到新塔模型时第一件事

```
1. 看 Fluid Package → 排除液液可能性
2. 看塔类型（Design Tab 顶部）→ 确认类型
3. 看 Phase 标签 → 确认相态
```

### 2. 胺液塔专用检查

```
1. 应该是 Reboiled Absorber（顶部无冷凝器）
2. Reflux Ratio 应该很低（0.1-0.5）
3. 顶部温度应接近进料富液温度（不是 25°C 默认估计）
4. 底部温度应接近水的沸点 + 压头
```