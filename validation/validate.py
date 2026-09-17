#!/usr/bin/env python3
import json, os, sys, numpy as np
OUTPUT_DIR = '/root/private_data/glacier_fall/output'
CONFIG_PATH = '/root/private_data/glacier_fall/config/parameters.json'
with open(CONFIG_PATH) as f:
    config = json.load(f)
with open(os.path.join(OUTPUT_DIR, 'analytical_baseline.json')) as f:
    baseline = json.load(f)
with open(os.path.join(OUTPUT_DIR, 'result.json')) as f:
    result = json.load(f)
print('=' * 60)
print('VALIDATION REPORT')
print('=' * 60)
checks = []
checks.append(('Contact detected', result['contact_detected'], True))
checks.append(('Contact time > 0', result['contact_time'] > 0, True))
checks.append(('Max contacts > 0', result['max_contacts'] > 0, True))
mgh = baseline['mgh']
friction_work = baseline['friction_work']
ke_impact_analytical = baseline['ke_impact']
ke_impact_sim = 0.5 * config['mass'] * result['final_vy']**2
energy_error = abs(ke_impact_sim - ke_impact_analytical) / ke_impact_analytical * 100
checks.append((f'KE at impact (sim={ke_impact_sim:.1f}J, analytical={ke_impact_analytical:.1f}J)', energy_error < 20, True))
print(f'\nAnalytical:')
print(f'  Acceleration: {baseline["a"]:.4f} m/s^2')
print(f'  Time to impact: {baseline["t_slope"]:.4f} s')
print(f'  Impact velocity: {baseline["v_impact"]:.4f} m/s')
print(f'\nSimulation:')
print(f'  Contact time: {result["contact_time"]:.4f} s')
print(f'  Final velocity: {result["final_vy"]:.4f} m/s')
print(f'  KE at impact: {ke_impact_sim:.1f} J')
print(f'  Max contacts: {result["max_contacts"]}')
print(f'\nEnergy check:')
print(f'  mgh = {mgh:.1f} J')
print(f'  Friction work = {friction_work:.1f} J')
print(f'  KE impact (analytical) = {ke_impact_analytical:.1f} J')
print(f'  KE impact (simulation) = {ke_impact_sim:.1f} J')
print(f'  Error = {energy_error:.1f}%')
print(f'\nValidation checks:')
passed = 0
for name, actual, expected in checks:
    status = 'PASS' if actual == expected else 'FAIL'
    if status == 'PASS':
        passed += 1
    print(f'  [{status}] {name}')
print(f'\nTotal: {passed}/{len(checks)} checks passed')
if passed == len(checks):
    print('VALIDATION PASSED')
else:
    print('VALIDATION FAILED - see details above')
sys.exit(0 if passed == len(checks) else 1)
