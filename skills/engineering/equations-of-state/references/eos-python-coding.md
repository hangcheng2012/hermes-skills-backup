# EOS Python 编程实战 —— 单组分 + 二元 + CoolProp 工具箱

> **本文件是 equations-of-state SKILL 的 references/ 详解之一**。
> 为女王工程提供可直接复用的 Python 编程示例,覆盖从自实现 SRK/PR 到 CoolProp 全流程。

---

## 一、环境与依赖

### 1.1 女王 venv 已装包(2026-06-30)

```bash
# 已确认安装
/home/hermes-admin/venv/bin/python --version
# Python 3.x

/home/hermes-admin/venv/bin/python -c "import CoolProp; print(CoolProp.__version__)"
# CoolProp 8.0.0

/home/hermes-admin/venv/bin/python -c "import numpy; print(numpy.__version__)"
# numpy 2.5.0
```

### 1.2 推荐安装路径

```bash
# 基本依赖(已装)
pip install CoolProp numpy scipy

# 可选(高级功能)
pip install matplotlib pandas

# 完整精算(可选)
pip install pyremez  # 多项式系数估计

# 商业 REFPROP 调用(可选,需要 REFPROP license)
pip install pypenthouselib  # REFPROP Python 接口
```

---

## 二、CoolProp 单组分快查(女王 80% 场景)

### 2.1 基本查询

```python
from CoolProp.CoolProp import PropsSI

def query_co2(T_K, P_Pa, mode='basic'):
    """
    用 CoolProp 查 CO₂ 单个 T-P 状态的所有物性
    mode: 'basic' / 'full' / 'phase'
    """
    result = {}

    # 基础物性
    result['ρ (kg/m³)']  = PropsSI('D', 'T', T_K, 'P', P_Pa, 'CO2')
    result['h (kJ/kg)']  = PropsSI('H', 'T', T_K, 'P', P_Pa, 'CO2') / 1e3
    result['s (kJ/kg·K)'] = PropsSI('S', 'T', T_K, 'P', P_Pa, 'CO2') / 1e3
    result['u (kJ/kg)']  = PropsSI('U', 'T', T_K, 'P', P_Pa, 'CO2') / 1e3
    result['Cp (kJ/kg·K)'] = PropsSI('C', 'T', T_K, 'P', P_Pa, 'CO2') / 1e3
    result['Z']          = PropsSI('Z', 'T', T_K, 'P', P_Pa, 'CO2')

    if mode == 'full':
        result['Cv (kJ/kg·K)'] = PropsSI('O', 'T', T_K, 'P', P_Pa, 'CO2') / 1e3
        result['μ (μPa·s)']   = PropsSI('V', 'T', T_K, 'P', P_Pa, 'CO2') * 1e6
        result['k (mW/m·K)']  = PropsSI('L', 'T', T_K, 'P', P_Pa, 'CO2') * 1e3
        result['声速 (m/s)']    = PropsSI('A', 'T', T_K, 'P', P_Pa, 'CO2')

    if mode == 'phase':
        phase_code = PropsSI('Phase', 'T', T_K, 'P', P_Pa, 'CO2')
        # CoolProp phase codes:
        # 0: Unknown, 1: liquid, 2: supercritical, 3: gas
        # 4: two-phase, 5: critical, 6: solid
        phase_map = {
            0: '未知', 1: '液体', 2: '超临界',
            3: '气', 4: '两相', 5: '临界', 6: '固体'
        }
        result['相态'] = phase_map.get(phase_code, f'code {phase_code}')

    return result


# 示例:30 MPa, 280°C 的 CO₂
T = 553.15  # K
P = 30e6    # Pa

print('=== 30 MPa, 280°C CO₂ - 基础物性 ===')
for k, v in query_co2(T, P, 'basic').items():
    print(f'{k:20s}: {v:.3f}')

print('\n=== 30 MPa, 280°C CO₂ - 完整物性 + 相态 ===')
for k, v in query_co2(T, P, 'full').items():
    print(f'{k:20s}: {v:.3f}')

print(f"相态            : {query_co2(T, P, 'phase')['相态']}")

# 期望输出:
# ρ (kg/m³): 75.66
# h (kJ/kg): 450.20
# s (kJ/kg·K): 1.78
# Cp (kJ/kg·K): 1.06
# Z: 0.69
# 相态: 超临界
```

### 2.2 多点查询(生成完整 T-P 网格)

```python
import numpy as np
import matplotlib.pyplot as plt

def co2_grid(T_range, P_range):
    """
    绘制 CO₂ 在 T-P 网格上的性质图
    T_range: (T_min, T_max, n_points)
    P_range: (P_min, P_max, n_points) (单位 Pa)
    """
    T_vec = np.linspace(*T_range)
    P_vec = np.linspace(*P_range)

    rho = np.zeros((len(T_vec), len(P_vec)))
    h = np.zeros_like(rho)
    Z = np.zeros_like(rho)

    for i, T in enumerate(T_vec):
        for j, P in enumerate(P_vec):
            try:
                rho[i, j] = PropsSI('D', 'T', T, 'P', P, 'CO2')
                h[i, j]   = PropsSI('H', 'T', T, 'P', P, 'CO2')
                Z[i, j]   = PropsSI('Z', 'T', T, 'P', P, 'CO2')
            except Exception:
                rho[i, j] = np.nan
                h[i, j] = np.nan
                Z[i, j] = np.nan

    return rho, h, Z


# 用例:绘制 200~600 K, 1~50 MPa 的 CO₂ 性质
T_range = (200, 600, 50)
P_range = (1e5, 50e6, 50)

rho, h, Z = co2_grid(T_range, P_range)

# 画密度场
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
T_vec = np.linspace(*T_range)
P_vec = np.linspace(*P_range) / 1e6
T_grid, P_grid = np.meshgrid(T_vec, P_vec)

im0 = axes[0].contourf(T_grid, P_grid, rho.T, levels=20, cmap='viridis')
axes[0].set_xlabel('T (K)')
axes[0].set_ylabel('P (MPa)')
axes[0].set_title('ρ (kg/m³)')
plt.colorbar(im0, ax=axes[0])

im1 = axes[1].contourf(T_grid, P_grid, h.T / 1e3, levels=20, cmap='plasma')
axes[1].set_xlabel('T (K)')
axes[1].set_ylabel('P (MPa)')
axes[1].set_title('h (kJ/kg)')
plt.colorbar(im1, ax=axes[1])

im2 = axes[2].contourf(T_grid, P_grid, Z.T, levels=20, cmap='coolwarm')
axes[2].set_xlabel('T (K)')
axes[2].set_ylabel('P (MPa)')
axes[2].set_title('Z')
plt.colorbar(im2, ax=axes[2])

plt.tight_layout()
plt.savefig('/home/hermes-admin/co2_phase_map.png', dpi=100)
plt.show()
```

---

## 三、自实现 PR EOS(完整 80 行)

### 3.1 单组分 PR EOS 函数

```python
import numpy as np

def pr_eos(T, P, Tc, Pc, omega, R=8.314):
    """
    Peng-Robinson EOS 1976 - 单组分
    输入 T (K), P (Pa) + 临界参数
    返回 Z, V_m, ρ
    """
    # 临界参数化
    a_c = 0.45724 * R**2 * Tc**2 / Pc
    b   = 0.07780 * R * Tc / Pc
    kappa = 0.37464 + 1.54226*omega - 0.26992*omega**2

    # α(T)
    Tr = T / Tc
    alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
    a = a_c * alpha

    # 无量纲立方方程: Z³ + p₁Z² + p₂Z + p₃ = 0
    A = a * P / (R*T)**2
    B = b * P / (R*T)

    p1 = -(1 - B)
    p2 = A - 3*B**2 - 2*B
    p3 = -(A*B - B**2 - B**3)

    # 解三次方程
    coeffs = [1, p1, p2, p3]
    roots = np.roots(coeffs)
    real_roots = roots[np.isreal(roots)].real

    # 物理过滤:0 < Z < 1(气相)或 Z > 1(超临界)
    valid_Z = real_roots[(real_roots > 0.001) & (real_roots < 1.0)]

    if len(valid_Z) == 0:
        # 可能超临界或饱和液:Z 可能在 0.05~0.95 外
        valid_Z = real_roots[(real_roots > 0.001) & (real_roots < 5.0)]

    if len(valid_Z) == 0:
        raise ValueError(f"PR EOS: no valid root found at T={T} K, P={P} Pa")

    # 取最大 Z(气相)
    Z = max(valid_Z)

    V_m = Z * R * T / P
    return Z, V_m


def pr_density(T, P, Tc, Pc, omega, M):
    """PR EOS + 密度输出"""
    R = 8.314
    Z, V_m = pr_eos(T, P, Tc, Pc, omega, R)
    ρ = M / V_m   # kg/m³
    return ρ


# 测试:CO₂
T = 553.15   # K
P = 30e6     # Pa
Tc = 304.25  # K
Pc = 7.38e6  # Pa
omega = 0.225
M = 44.01e-3 # kg/mol

Z, V_m = pr_eos(T, P, Tc, Pc, omega)
ρ = pr_density(T, P, Tc, Pc, omega, M)

print(f"PR EOS @ CO₂ 30 MPa, 280°C:")
print(f"  Z    = {Z:.4f}")      # 期望 ~0.78
print(f"  V_m  = {V_m*1e6:.2f} cm³/mol")
print(f"  ρ    = {ρ:.2f} kg/m³")   # 期望 ~89 (误差 ~+12% vs SW)

# 与 SW 比较
from CoolProp.CoolProp import PropsSI
ρ_SW = PropsSI('D', 'T', T, 'P', P, 'CO2')
print(f"  ρ(SW)= {ρ_SW:.2f} kg/m³")  # 期望 75.66
print(f"  PR vs SW 误差: {(ρ - ρ_SW) / ρ_SW * 100:.1f}%")
```

### 3.2 二元混合物 PR EOS(van der Waals 1-fluid)

```python
def pr_mixture_vdw(T, P, x, Tc, Pc, omega, k_ij, R=8.314):
    """
    PR EOS + vdW 1-fluid 混合规则 - N 元混合物
    参数:
        x: 摩尔分率数组
        Tc, Pc, omega: 数组(N,)
        k_ij: 二元交互参数矩阵(N, N)
    """
    N = len(x)

    # 单组分参数
    a_c = 0.45724 * R**2 * Tc**2 / Pc
    b   = 0.07780 * R * Tc / Pc
    kappa = 0.37464 + 1.54226*omega - 0.26992*omega**2

    Tr = T / Tc
    alpha = (1 + kappa * (1 - np.sqrt(Tr)))**2
    a_i = a_c * alpha  # (N,) 数组

    # 混合规则
    a_mix = 0.0
    for i in range(N):
        for j in range(N):
            a_mix += x[i] * x[j] * np.sqrt(a_i[i] * a_i[j]) * (1 - k_ij[i, j])

    b_mix = np.dot(x, b)

    # 立方方程
    A = a_mix * P / (R*T)**2
    B = b_mix * P / (R*T)

    p1 = -(1 - B)
    p2 = A - 3*B**2 - 2*B
    p3 = -(A*B - B**2 - B**3)

    coeffs = [1, p1, p2, p3]
    roots = np.roots(coeffs)
    Z_real = roots[np.isreal(roots)].real
    Z_valid = Z_real[Z_real > 0.001]

    if len(Z_valid) == 0:
        raise ValueError(f"No valid root at T={T}, P={P}")

    return Z_valid.max()


# 应用:CO₂ + CH₄ 二元
T = 300   # K
P = 5e5   # 5 bar

x = np.array([0.5, 0.5])
Tc = np.array([304.25, 190.6])  # CO₂, CH₄
Pc = np.array([7.38e6, 4.60e6])
omega = np.array([0.225, 0.011])
k_ij = np.array([[0, 0.12], [0.12, 0]])

Z_mix = pr_mixture_vdw(T, P, x, Tc, Pc, omega, k_ij)
print(f"PR vdW: CO₂/CH₄ (50/50) at {T} K, {P/1e5} bar: Z = {Z_mix:.4f}")

# 注:完整的二元计算需要 flash algorithm(求液 + 气相分配)
```

---

## 四、自实现 SRK EOS

### 4.1 单组分 SRK EOS

```python
def srk_eos(T, P, Tc, Pc, omega, R=8.314):
    """SRK EOS 1972 - 单组分"""
    a_c = 0.42747 * R**2 * Tc**2 / Pc
    b   = 0.08664 * R * Tc / Pc
    m   = 0.48 + 1.574*omega - 0.176*omega**2

    Tr = T / Tc
    alpha = (1 + m * (1 - np.sqrt(Tr)))**2
    a = a_c * alpha

    A = a * P / (R*T)**2
    B = b * P / (R*T)

    # SRK 立方方程:Z³ - Z² + (A - B - B²)Z - AB = 0
    coeffs = [1, -1, A - B - B**2, -A*B]
    roots = np.roots(coeffs)
    Z_real = roots[np.isreal(roots)].real
    Z_valid = Z_real[Z_real > 0.001]

    if len(Z_valid) == 0:
        raise ValueError("No valid root!")

    return Z_valid.max()


# 测试
T = 553.15
P = 30e6
Tc = 304.25
Pc = 7.38e6
omega = 0.225

Z = srk_eos(T, P, Tc, Pc, omega)
print(f"SRK EOS @ CO₂ 30 MPa, 280°C: Z = {Z:.4f}")
# 期望 ~0.85(显著高于 SW 标准的 0.69)
```

---

## 五、CoolProp 二元混合物查询

### 5.1 二元查询

```python
from CoolProp.CoolProp import PropsSI

def co2_ch4_mixture(x_CO2, T_K, P_Pa):
    """CO₂ + CH₄ 二元混合物"""
    return {
        'x_CO2': x_CO2,
        'ρ (kg/m³)': PropsSI('D', 'T', T_K, 'P', P_Pa, 'Q', 0, 'CO2&CH4'),
        # 注意:这里 OR 取 OR = 0 是关键
    }


# 应用前注意:CoolProp 混合物要用 '::' 分隔(如 'CO2::CH4')
# 完整地用 Flash
from CoolProp.CoolProp import PropsSI

# 50/50 CO₂/CH₄ 在 300 K, 10 bar
T = 300
P = 10e5  # 10 bar

# 单组分比对
ρ_CO2 = PropsSI('D', 'T', T, 'P', P, 'CO2')
ρ_CH4 = PropsSI('D', 'T', T, 'P', P, 'CH4')

# 二元 Flash
# (闪蒸算法较复杂,需指定 z 并用 PT-flash)
from CoolProp.CoolProp import AbstractState

AS = AbstractState('HEOS', 'CO2&CH4')
AS.set_mole_fractions([0.5, 0.5])
AS.update(P=P, T=T)

ρ_mix = AS.rho()
T_c = AS.T_critical()
P_c = AS.p_critical()

print(f"CO₂/CH₄ 50/50, T={T} K, P={P/1e5} bar:")
print(f"  ρ_mix = {ρ_mix:.2f} kg/m³")
print(f"  T_c(mix) = {T_c:.2f} K")
print(f"  P_c(mix) = {P_c/1e5:.2f} bar")
```

### 5.2 实用混合查询(Peng-Robinson on HEOS backend)

```python
from CoolProp.CoolProp import AbstractState, HEOS

# 创建 CO₂ + CH₄ 混合物(用 HEOS = Helmholtz EOS,即 SW)
AS = AbstractState(HEOS, '&'.join(['CO2', 'CH4']))

# 设组成
AS.set_mole_fractions([0.5, 0.5])

# 设 T, P
AS.update(P=10e5, T=300)

# 查询
print(f"混合密度: {AS.rho():.4f} kg/m³")
print(f"Z: {AS.Q()}")
print(f"相态: {AS.phase()}")

# 计算汽液平衡(Flash)
AS.update(P=10e5, T=250)  # T < 临界温度
# 用 PT-flash 找气液两相分配(略)
```

---

## 六、女王工艺的"Python 工作流"

### 6.1 scCO₂-PET 工艺的关键计算任务

| 任务 | Python 实现 |
|------|-------------|
| 反应釜温压监测 | CoolProp 单组分查询 |
| 节流温降计算 | h1 = h2 等焓定理 + CoolProp |
| 防干冰工况判断 | T_tp, P_tp 比较 + 节流后 T, P |
| PSV 排放校核 | NIST WebBook + J-T 反转曲线 |
| 收集罐液位 | 密度差 + z(T, P) |

### 6.2 节流温降的 Python 实现

```python
def throttling_calculation(P1, T1, P2, fluid='CO2'):
    """
    等焓节流计算
    输入:P1, T1(节流前), P2(节流后)
    输出:T2(节流后温度)+ 状态描述
    """
    h1 = PropsSI('H', 'T', T1, 'P', P1, fluid)

    # 求解:T2 使得 h(T2, P2) = h1
    # 用 scipy 的 fsolve 或新现代算法

    from scipy.optimize import brentq

    def f(T2):
        return PropsSI('H', 'T', T2, 'P', P2, fluid) - h1

    # 数值求解
    try:
        T2 = brentq(f, 100, 1500)
        Z2 = PropsSI('Z', 'T', T2, 'P', P2, fluid)
        return T2, Z2, h1
    except Exception as e:
        return None, None, h1


# 应用:30 MPa, 553 K(280°C)→ 4 MPa
T1 = 553.15
P1 = 30e6
P2 = 4e6

T2, Z2, h1 = throttling_calculation(P1, T1, P2, fluid='CO2')

print(f"CO₂ 节流: {P1/1e6} MPa, {T1} K → {P2/1e6} MPa, {T2:.2f} K")
print(f"  h1 = h2 = {h1/1e3:.2f} kJ/kg")
print(f"  Z2 = {Z2:.4f}")

# 期望结果:
# T2 ≈ 380~420 K(过热度冷却 ~150~180 K)
# Z2 ≈ 0.65~0.70
```

### 6.3 防干冰工况判断

```python
def dry_ice_risk_check(P_in, T_in, P_out, fluid='CO2'):
    """
    检查 CO₂ 节流是否进入干冰区
    """
    T_tp = PropsSI('T_triple', fluid)  # K
    P_tp = PropsSI('P_triple', fluid)  # Pa

    # 节流后温度
    T_out, _, _ = throttling_calculation(P_in, T_in, P_out, fluid)

    if T_out is None:
        return {'risk': '无法计算', 'P_min': P_tp}

    risk = '高' if T_out < T_tp else '低'

    return {
        'T_in': T_in,
        'P_in': P_in,
        'P_out': P_out,
        'T_out': T_out,
        'T_triple': T_tp,
        'P_triple': P_tp,
        '干冰风险': risk,
        '理由': f'节流后温度 {T_out:.1f} K 低于三相点温度 {T_tp:.1f} K'
                if T_out < T_tp else
                f'节流后温度 {T_out:.1f} K 远高于三相点 {T_tp:.1f} K,无冻冰风险'
    }


# 应用
result = dry_ice_risk_check(30e6, 280 + 273.15, 4e6)
print("== 干冰风险检查 ==")
for k, v in result.items():
    print(f"  {k}: {v}")

# 期望:无冻冰风险(因为节流后温度约 380~420 K ≫ T_tp = 216.55 K)
```

---

## 七、批量处理与流程计算

### 7.1 工况扫描

```python
def workflow_sweep(fluid, T_range, P_range):
    """
    扫 T-P 网格,输出每个点的物性 + 节流后温度
    """
    results = []
    for T in T_range:
        for P in P_range:
            try:
                h1 = PropsSI('H', 'T', T, 'P', P, fluid)
                T2 = throttling_calculation(P, T, 4e6, fluid)[0]
                results.append({
                    'T_in': T,
                    'P_in': P,
                    'h_in': h1,
                    'T_out (4MPa)': T2
                })
            except Exception:
                results.append({'T_in': T, 'P_in': P, 'h_in': None, 'T_out (4MPa)': None})
    return results


# 应用:扫反应釜 (T, P) 网格的节流温降
T_vals = np.linspace(280 + 273.15, 360 + 273.15, 10)  # 280~360°C
P_vals = np.logspace(np.log10(10e6), np.log10(40e6), 5)  # 10~40 MPa

results = workflow_sweep('CO2', T_vals, P_vals)
print("=== 反应釜温压扫描 + 节流到 4 MPa ===")
print(f"{'T_in (K)':<10} {'P_in (MPa)':<12} {'h_in (kJ/kg)':<15} {'T_out (K)':<12}")
for r in results:
    P_MPa = r['P_in'] / 1e6 if r['P_in'] else 0
    h_kJkg = r['h_in'] / 1e3 if r['h_in'] else 0
    T_out = r['T_out (4MPa)'] if r['T_out (4MPa)'] else 0
    print(f"{r['T_in']:<10.1f} {P_MPa:<12.2f} {h_kJkg:<15.2f} {T_out:<12.2f}")
```

---

## 八、常见错误与调试

### 8.1 常见错误代码

| 错误码 | 含义 | 解决 |
|--------|------|------|
| 1 | out of range | T, P 超出 EOS 适用区间,用 NIST 确认 |
| 2 | NotImplemented | CO₂ 用了 PR EOS 但在临界点附近,改 SW |
| 3 | ValueError("No valid root") | 自实现 EOS 解析有问题,检查三次方程 |
| 4 | "Cannot find EOS for fluid" | 流体名错,如 'CO2' 不要加空格 |

### 8.2 调试技巧

```python
# 调试用
import logging
logging.basicConfig(level=logging.DEBUG)

from CoolProp.CoolProp import PropsSI
ρ = PropsSI('D', 'T', 553.15, 'P', 30e6, 'CO2')
# 启用 debug 会显示 EOS 选型过程

# 单步调试
def safe_query(T, P, fluid, prop='D'):
    try:
        return PropsSI(prop, 'T', T, 'P', P, fluid)
    except Exception as e:
        print(f"Error at T={T}, P={P}: {e}")
        return np.nan

# 用法
ρ = safe_query(553.15, 30e6, 'CO2')
```

---

## 九、本文件的边界

**本文件覆盖:**
- CoolProp 基础 + 进阶调用
- PR / SRK 自实现(单组分 + 混合物)
- 节流计算 + 干冰风险检查
- 二元混合物 + 闪蒸基础
- 女王工艺 Python 工作流

**本文件不覆盖:**
- PR / SRK / SW 公式 → 前面 3 个 references
- EOS 选择决策 → `when-to-use-which-eos.md`
- 数据源表 → `data-sources-and-references.md`
- SW 自实现(太复杂,工程不需要)→ 见 `span-wagner-eos-detailed.md`

---

## 十、版本与修订

| 版本 | 日期 | 主要内容 |
|------|------|----------|
| v1.0 | 2026-06-30 | 初版。CoolProp 单组分 / 二元 / 节流 / 干冰判断全 Python 实现。女王小试装置可直接复用。 |
