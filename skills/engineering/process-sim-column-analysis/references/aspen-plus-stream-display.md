# Aspen Plus 流股显示与鼠标悬停设置

女王问 Aspen 中鼠标停留在流股上显示的内容在哪里调出。本文档覆盖 Aspen Plus 流股显示设置的所有路径。

## 一、简短回答

Aspen Plus 流股显示的内容（流程图上常显 + 鼠标悬停 popup）共享**同一套 Display Options 配置**，控制入口：

**新版 Ribbon 界面 (V8.0+)：**
```
Flowsheet → Modify 选项卡 → Display Options 按钮
```

**经典菜单界面：**
```
View → Global Data（控制常显）
Format → Stream Format（控制格式）
Tools → Customize（深度自定义）
```

**字段定义核心（影响悬停 popup 内容）：**
```
Data Browser → Setup → Report Options → Stream
```

## 二、详细操作

### 路径 1：Display Options（最常用）

**新版 Ribbon (V8.0+):**
1. 顶部菜单 → **Flowsheet** 标签
2. 找到 **Modify** 子标签（或直接在 Ribbon 找 Display Options 按钮）
3. 点 **Display Options** 按钮
4. 弹出 Display Options 对话框：

| 区域 | 作用 |
|------|------|
| Display 下拉框 | All Streams（所有流股）/ Streams（指定流股）|
| 字段勾选区 | 选要显示的字段：温度、压力、流量、组分流量、焓、密度等 |
| Format 子页 | 调小数位数（%.0f 不留小数，%.1f 一位小数）、单位制 |

**经典菜单：**
1. View → 勾选/取消 **Global Data**（流程图上常显）
2. Format → **Stream Format**（调小数位数、单位）
3. Tools → **Customize**（深度自定义字段）

### 路径 2：Report Options（深度自定义字段）

**路径：** `Data Browser → Setup → Report Options → Stream`

这里定义的是**报告和弹窗都会调用**的字段集合。改完后：
- 流程图常显内容更新
- 鼠标悬停 popup 内容更新
- Stream Table（报告）内容更新

### 路径 3：单位集调整

**路径：** `Data Browser → Setup → Units Sets`

选单位集（ENG / MET / SI-CBAR / METCBAR / METCKGGM / SI）：
- 改完后**全塔所有流股显示**同步更新
- 影响温度（T → °C/°F/K）、压力（MPa/bar/psia）、流量等单位

## 三、关键事实

### 1. 常显内容 = 悬停 popup 内容

Aspen Plus 里**流程图上始终显示的标签**和**鼠标悬停时弹出的 tooltip**，用的是**同一套 Display Options 配置**。改一处同步生效。

### 2. 单位集是全局联动

改 Units Sets（如 ENG → SI）后：
- 所有流股显示的温度、压力、流量单位自动切换
- 弹窗内容同步切换
- 不需要逐个流股手动调

### 3. 流股 vs 能量流股

- **Process Stream（流股）**：实线，显示 T/P/flow/composition
- **Heat Stream（能量流）**：虚线，只显示 Duty
- **Work Stream（功流）**：点划线，显示 Power

Aspen 的 Display Options 只对 Process Stream 生效。

## 四、常见操作快捷键

| 快捷键 | 作用 |
|--------|------|
| `Ctrl+H` | 隐藏/显示流股 ID |
| `Ctrl+J` | 重排流股路径 |
| `Ctrl+B` | 对齐流股 |

## 五、女王实战建议

### 出图（P&ID/PFD 附件）的标准流股标签设置

按女王 P&ID v6.9 出图规范，推荐：

| 字段 | 显示 | 单位 |
|------|------|------|
| Temperature | ✅ | °C |
| Pressure | ✅ | MPa(G) |
| Mass Flow | ✅ | kg/h |
| Molar Flow | ❌（避免重复）| - |
| Vapour Fraction | 必要时 ✅ | - |
| Density | ❌（省位）| - |

### 操作序列

1. Flowsheet → Modify → **Display Options**
2. Display: All Streams
3. 勾选 Temperature、Pressure、Mass Flow
4. Format → 温度 "%.1f"，压力 "%.3f"，流量 "%.0f"
5. OK → 流程图立即刷新
6. View → Global Data 确认常显开关打开

## 六、与 HYSYS 的对比（女王同时用两个软件时）

| 功能 | Aspen Plus | HYSYS |
|------|-----------|-------|
| 流程图常显控制 | Flowsheet → Modify → Display Options | View → Workbook → Customize |
| 鼠标悬停 popup | 同上共享配置 | Display Options 同理 |
| 字段定制 | Setup → Report Options | Table Properties / Modify Table |
| 单位集 | Setup → Units Sets | Tools → Preferences → Units |

跨软件迁移注意：HYSYS 没有"鼠标悬停显示"功能（信息已在 stream 表中），Aspen Plus 才有 tooltip。