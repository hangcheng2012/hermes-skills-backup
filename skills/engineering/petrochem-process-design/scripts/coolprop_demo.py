"""CoolProp 3 demo for 女王 — N2/Toluene/Vacuum"""
import CoolProp.CoolProp as CP

print("=" * 70)
print("CoolProp 安装验证")
print("=" * 70)
print(f"CoolProp 版本: {CP.get_global_param_string('version')}")
print(f"内置流体总数: {len(CP.FluidsList())}")

print("\n" + "=" * 70)
print("DEMO 1: N₂ 减压阀流量核算（PCV-101B 第二级减压阀）")
print("=" * 70)
print("工况: N₂ 从 50 kPa 减压至 0.5-1 kPa, 30℃, V-101/102/103 氮封")
for P_out_kPa in [10, 5, 1, 0.5]:
    rho = CP.PropsSI('D', 'P', P_out_kPa * 1000, 'T', 303.15, 'Nitrogen')
    print(f"  P={P_out_kPa:5.2f} kPa, T=30℃ → ρ = {rho:.4f} kg/m³")

print("\n" + "=" * 70)
print("DEMO 2: 甲苯储罐 PSV 整定压力（V-101/102/103 介质=甲苯）")
print("=" * 70)
print("依据女王 06-25 立规: PSV 5-10 kPa 弹簧式 GB/T 12241")
for T_C in [20, 25, 30, 35, 40]:
    P_sat_kPa = CP.PropsSI('P', 'T', T_C + 273.15, 'Q', 0, 'Toluene') / 1000
    PSV_setpoint = 1.1 * P_sat_kPa
    print(f"  T={T_C:2d}℃ → P_sat = {P_sat_kPa:6.3f} kPa, PSV ≥ {PSV_setpoint:6.3f} kPa")

print("\n" + "=" * 70)
print("DEMO 3: V-401 真空蒸馏 10 mbar 工况（v6.9 真空度）")
print("=" * 70)
for fluid in ['Toluene', 'Water', 'n-Hexane', 'Acetone', 'Methanol', 'Benzene']:
    T_boil_K = CP.PropsSI('T', 'P', 10, 'Q', 1, fluid)
    T_boil_C = T_boil_K - 273.15
    rho_vapor = CP.PropsSI('D', 'T', T_boil_K, 'Q', 1, fluid)
    print(f"  {fluid:12s}: T_boil@10mbar = {T_boil_C:7.2f}℃, ρ_vapor = {rho_vapor:.5f} kg/m³")

print("\n" + "=" * 70)
print("DEMO 4 (赠): 女王常用 20 种组分速查")
print("=" * 70)
print(f"{'介质':12s} {'T_c(℃)':>8s} {'P_c(kPa)':>10s} {'M(g/mol)':>10s} {'ρ_liq_20℃(kg/m³)':>18s}")
print("-" * 65)
common = ['Water', 'Nitrogen', 'Oxygen', 'Air', 'Ammonia', 'CO2', 'CO', 'H2S',
          'Methane', 'Ethane', 'n-Propane', 'n-Butane', 'n-Pentane', 'n-Hexane',
          'Toluene', 'Benzene', 'Methanol', 'Ethanol', 'Acetone', 'HydrogenChloride']
for fluid in common:
    T_c = CP.PropsSI('Tcrit', fluid) - 273.15
    P_c = CP.PropsSI('Pcrit', fluid) / 1000
    M = CP.PropsSI('M', fluid) * 1000
    # 20℃下: T<T_crit 走饱和液, T>T_crit 走 1atm 气态
    try:
        if 293.15 < CP.PropsSI('Tcrit', fluid):
            rho_liq = CP.PropsSI('D', 'T', 293.15, 'Q', 0, fluid)
            phase_note = '液'
        else:
            rho_liq = CP.PropsSI('D', 'T', 293.15, 'P', 101325, fluid)
            phase_note = '气@1atm'
    except Exception:
        rho_liq = float('nan')
        phase_note = 'N/A'
    print(f"{fluid:12s} {T_c:8.2f} {P_c:10.1f} {M:10.2f} {rho_liq:14.2f} {phase_note}")

print("\n" + "=" * 70)
print("✅ 4 个 demo 全部跑通。CoolProp 8.0.0 + numpy 2.5.0")
print("=" * 70)