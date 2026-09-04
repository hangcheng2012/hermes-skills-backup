# HYSYS Column Profile 自定义字段：详细操作手册

女王 07-18 实战总结。本文档按 HYSYS 版本分列加密度/粘度/自定义参数的全部路径，按可靠性排序。

## 一、核心结论

**HYSYS Column Profile 添加自定义字段（如气液密度、粘度）有 5 种路径，按可靠性从高到低：**

1. **Plots 页 → View Table**（100% 成功，无需任何 UI 定制）
2. **Column Profiles 页 → 右键数据格 → Table Properties**（官方主路径）
3. **顶部 Table 菜单 → Table Properties**（备选）
4. **Tools → Preferences → Property Sets**（自定义复用集）
5. **Spreadsheet Operation + 内部变量公式**（100% 成功，跨版本通用）

## 二、按 HYSYS 版本分列的菜单路径

### HYSYS V14（最新，Ribbon 界面）

| 操作 | 路径 |
|------|------|
| 进入 Column Profiles | 双击塔 → Performance → Column Profiles |
| 加密度列 | 右键数据格 → **Properties** → Columns → 顶部下拉框选 Transport Properties |
| View Graph 出图 | Performance → Plots → Transport Properties → View Graph |
| View Table 出数据表 | Performance → Plots → Transport Properties → View Table |

### HYSYS V12-V13

| 操作 | 路径 |
|------|------|
| 进入 Column Profiles | 双击塔 → Performance → Column Profiles |
| 加密度列 | 右键数据格 → **Format Table** 或 **Table Properties** |
| Ribbon 路径 | Home → Table → Format Table |

### HYSYS V10-V11

| 操作 | 路径 |
|------|------|
| 进入 Column Profiles | 双击塔 → Performance → Column Profiles |
| 加密度列 | 右键数据格 → **Modify Table…** |
| 菜单路径 | Table → Modify Table… 或 Format → Table… |

### HYSYS V8-V9（较旧，经典菜单）

| 操作 | 路径 |
|------|------|
| 进入 Column Profiles | 双击塔 → Performance → Column Profiles |
| 加密度列 | 菜单 → **Table** → **Table Properties** |
| 备用 | 选中表格 → **Alt + Enter** 打开属性 |

### HYSYS 2004 / V7（极旧版本）

| 操作 | 路径 |
|------|------|
| 进入 Column Profiles | 双击塔 → Performance |
| 加密度列 | 选中表格 → **Format** → **Table…** |
| 菜单 | 右键 → Format Table |

## 三、Table Properties 对话框内部结构

无论哪个版本，对话框通常包含 4 个标签：

| 标签 | 作用 |
|------|------|
| **Columns** ⭐ | 选字段。顶部下拉框：Temperature / Pressure / Flow / **Transport Properties** / Composition / Reactions / User Properties |
| **Rows** | 选塔板范围（含/不含冷凝器再沸器） |
| **Format** | 调小数位数、单位制 |
| **Filters** | Filter Setup 功能（数值过滤） |

### Columns 标签里加密度的具体步骤

1. 进 Columns 标签
2. 顶部下拉框选 **Transport Properties**（或 Physical Properties）
3. 下方字段列表刷新
4. 勾选：
   - ✅ Vapour Mass Density（气相质量密度）
   - ✅ Vapour Molar Density（气相摩尔密度）
   - ✅ Liquid Mass Density（液相质量密度）
   - ✅ Liquid Molar Density（液相摩尔密度）
   - ✅ Vapour Viscosity（气相粘度）
   - ✅ Liquid Viscosity（液相粘度）
   - ✅ Surface Tension（表面张力）
   - ✅ Thermal Conductivity（热导率）
5. 点 Add → 字段进右侧"已选"
6. 点 OK / Apply

## 四、Plots 页面：最快的查密度路径

**女王实战首选**，因为 Plots 页面已内置密度字段，无需任何定制。

### Plots 页面 Tray by Tray Properties 列表

HYSYS 官方文档原文确认包含：
> "Select a profile from the list in the Tray by Tray Properties group. The choices include: Temperature, Pressure, Flow, **MW, Dens, Visc.**, Composition, K Value"

**Dens = Density（密度）**
**Visc = Viscosity（粘度）**
**MW = Molecular Weight（分子量）**

### 操作步骤

1. Performance → Plots
2. **Tray by Tray Properties** 框里选 **Transport Properties**
3. 点 **View Table...** → 弹出新表，含密度/粘度数据
4. 点 **View Graph...** → 弹出剖面图

## 五、100% 通用后备：Spreadsheet Operation

**任何 HYSYS 版本、任何 UI 失败时的终极方案。**

### 操作步骤

1. 主流程图 → Model Palette → **Logicals → Spreadsheet**
2. 命名如 "T-101_Profile"
3. 在表格的 Import 列写公式：

| 位置 | 公式（内部变量） |
|------|-----------------|
| A1 | `T-101.Stage[1].VapourPhase.MassDensity` |
| A2 | `T-101.Stage[2].VapourPhase.MassDensity` |
| ... | 复制粘贴，修改 Stage 编号 |
| B1 | `T-101.Stage[1].LiquidPhase.MassDensity` |
| C1 | `T-101.Stage[1].VapourPhase.Viscosity` |
| D1 | `T-101.Stage[1].LiquidPhase.Viscosity` |
| E1 | `T-101.Stage[1].VapourPhase.SurfaceTension` |
| F1 | `T-101.Stage[1].Temperature` |
| G1 | `T-101.Stage[1].Pressure` |
| H1 | `T-101.Stage[1].VapourPhase.MassFlow` |
| I1 | `T-101.Stage[1].LiquidPhase.MassFlow` |

4. HYSYS 自动算出 Export 列（kg/m³, cP 等）
5. File → Export → CSV/Excel

### 内部变量命名规则

```
<ColumnName>.Stage[<N>].<Phase>.<Property>
```

- **ColumnName**：塔 ID，如 `T-101`
- **Stage[N]**：塔板号，HYSYS 默认 1 = 顶部（Condenser 之后），N 递增向下
- **Phase**：`VapourPhase` / `LiquidPhase` / `LightLiquidPhase`（液液萃取轻相）/ `HeavyLiquidPhase`（液液萃取重相）
- **Property**：`MassDensity` / `MolarDensity` / `Viscosity` / `MassFlow` / `Temperature` / `Pressure` / `SurfaceTension` / `ThermalConductivity` / `Cp` / `MolecularWeight` / `MassFractionComp<Name>`

## 六、自定义 Property Set（Tools → Preferences）

适合反复用同一组字段的场景。

### 操作步骤

1. **Tools → Preferences → Property Sets**
2. **新建**（Create New），命名如 "MyTrayProfile"
3. 在字段库手动添加内部变量（同上 Spreadsheet 语法）
4. 保存
5. 回到 Column Profiles 表 → Table Properties → Columns → 顶部 Property Set 下拉框选 "MyTrayProfile"
6. 自定义字段一次性出现

## 七、Filter Setup 对话框的真相

**容易踩坑**：Filter Setup 不是用来"加字段"的，是用来"显示/隐藏已有字段"的。

### 操作步骤

1. Column Profiles 表 → 表头任意位置右键
2. 选 **Filter Setup…**
3. 弹出对话框，列出"当前已显示"的列
4. 勾选/取消勾选 → Apply Filter → 该列显隐
5. **不能新增字段**

### Filter Setup vs Table Properties 对比

| 功能 | Filter Setup | Table Properties |
|------|-------------|------------------|
| 隐藏现有列 | ✅ | ✅ |
| 新增字段 | ❌ | ✅ |
| 改显示顺序 | ❌ | ✅ |
| 调小数位 | ❌ | ✅ |

## 八、女王实战检查清单（07-18 总结）

当 T-101 出现以下异常时按此清单排查：

- [ ] 顶部温度黄高亮（≈25°C）→ 调塔类型，去 Condenser
- [ ] Reflux Ratio 异常高（>5）→ 检查是否真需要外回流
- [ ] 塔内温度跨度 < 8°C → 检查进料组分是否接近平衡
- [ ] 黄高亮长期不消失 → Parameters → Solver 调 Damping Factor 到 0.25-0.5
- [ ] 右键没 Table Properties → **改点数据格**，别点空白
- [ ] 上面全失败 → 用 Spreadsheet Operation（100% 通用）

## 九、跨版本最大坑

女王 07-18 实际踩坑：**HYSYS V10 之后，菜单从"右键弹出"变成"顶部 Ribbon"**。如果女王用的是 V10 之前的版本，主路径在顶部菜单；V10 之后优先试 Ribbon 按钮。

判断方法：**看顶部是否有 Ribbon 功能区标签（Home/Insert/Page Layout 等）**。
- 有 Ribbon → V10+，主路径 Ribbon
- 无 Ribbon → V8-，主路径顶部菜单