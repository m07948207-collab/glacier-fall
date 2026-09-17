#!/usr/bin/env python3
"""
Minimal collision tests A/B/C
A: Sphere -> Box free fall
B: Box -> Box collision
C: Static slope -> dynamic block
"""
import os, sys, json
sys.path.insert(0, '/root/private_data/chrono/build-py311/bin')
import pychrono as chrono
import numpy as np

OUTPUT_DIR = '/root/private_data/glacier_fall/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

CFG = {
    'gravity': 9.81,
    'dt': 1e-4,
    't_max': 3.0,
    'friction': 0.3,
    'restitution': 0.5,
}

def make_system():
    sys = chrono.ChSystemNSC()
    sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -CFG['gravity'], 0))
    sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    cs = sys.GetCollisionSystem()
    if cs:
        cs.Initialize()
    mat = chrono.ChContactMaterial_DefaultMaterial(chrono.ChContactMethod_NSC)
    mat.SetFriction(CFG['friction'])
    mat.SetRestitution(CFG['restitution'])
    return sys, mat

def step_and_collect(sys, body, dt):
    t = 0.0
    max_pen = 0.0
    contact_steps = 0
    while t < CFG['t_max']:
        sys.DoStepDynamics(dt)
        t += dt
        cc = sys.GetContactContainer()
        n = cc.GetNumContacts() if cc else 0
        if n > 0:
            contact_steps += 1
            for i in range(n):
                c = cc.GetContact(i)
                try:
                    d = c.GetPenetrationDepth()
                    if d > max_pen:
                        max_pen = d
                except Exception:
                    pass
        if contact_steps > 0 and t > 0.05:
            break
    return contact_steps, max_pen

# Test A
print('=' * 60)
print('TEST A: Sphere -> Box')
print('=' * 60)
sysA, matA = make_system()
sphere = chrono.ChBodyEasySphere(0.5, 500.0, True, True)
sphere.SetPos(chrono.ChVector3d(0.0, 3.0, 0.0))
sphere.SetLinVel(chrono.ChVector3d(0.0, 0.0, 0.0))
sysA.AddBody(sphere)
box = chrono.ChBodyEasyBox(4.0, 4.0, 4.0, 1000.0, True, True)
box.SetPos(chrono.ChVector3d(0.0, -1.0, 0.0))
box.SetFixed(True)
sysA.AddBody(box)
cc = sysA.GetContactContainer()
print('Contacts before step:', cc.GetNumContacts() if cc else 0)
steps_A, pen_A = step_and_collect(sysA, sphere, CFG['dt'])
print('Contact steps:', steps_A)
print('Max penetration:', pen_A)
print('Final pos:', (sphere.GetPos().x, sphere.GetPos().y, sphere.GetPos().z))
print('Final vel:', (sphere.GetLinVel().x, sphere.GetLinVel().y, sphere.GetLinVel().z))

# Test B
print()
print('=' * 60)
print('TEST B: Box -> Box')
print('=' * 60)
sysB, matB = make_system()
b1 = chrono.ChBodyEasyBox(1.0, 1.0, 1.0, 1000.0, True, True)
b1.SetPos(chrono.ChVector3d(0.0, 2.0, 0.0))
b1.SetLinVel(chrono.ChVector3d(0.0, 0.0, 0.0))
sysB.AddBody(b1)
b2 = chrono.ChBodyEasyBox(1.0, 1.0, 1.0, 10000.0, True, True)
b2.SetPos(chrono.ChVector3d(0.0, 0.5, 0.0))
b2.SetFixed(True)
sysB.AddBody(b2)
ccB = sysB.GetContactContainer()
print('Contacts before step:', ccB.GetNumContacts() if ccB else 0)
steps_B, pen_B = step_and_collect(sysB, b1, CFG['dt'])
print('Contact steps:', steps_B)
print('Max penetration:', pen_B)
print('Final pos:', (b1.GetPos().x, b1.GetPos().y, b1.GetPos().z))
print('Final vel:', (b1.GetLinVel().x, b1.GetLinVel().y, b1.GetLinVel().z))

# Test C
print()
print('=' * 60)
print('TEST C: Static slope -> dynamic block')
print('=' * 60)
sysC, matC = make_system()
slope = chrono.ChBodyEasyBox(10.0, 0.5, 4.0, 1000.0, True, True)
slope.SetPos(chrono.ChVector3d(2.0, 0.0, 0.0))
m = chrono.ChMatrix33d()
m.SetFromCardanAnglesZYX(chrono.ChVector3d(0.0, -0.615, 0.0))
slope.SetRot(m)
slope.SetFixed(True)
sysC.AddBody(slope)
blk = chrono.ChBodyEasyBox(1.0, 1.0, 1.0, 100.0, True, True)
blk.SetPos(chrono.ChVector3d(0.0, 2.0, 0.0))
blk.SetLinVel(chrono.ChVector3d(0.0, 0.0, 0.0))
sysC.AddBody(blk)
ccC = sysC.GetContactContainer()
print('Contacts before step:', ccC.GetNumContacts() if ccC else 0)
steps_C, pen_C = step_and_collect(sysC, blk, CFG['dt'])
print('Contact steps:', steps_C)
print('Max penetration:', pen_C)
print('Final pos:', (blk.GetPos().x, blk.GetPos().y, blk.GetPos().z))
print('Final vel:', (blk.GetLinVel().x, blk.GetLinVel().y, blk.GetLinVel().z))

# Summary
print()
print('=' * 60)
print('SUMMARY')
print('=' * 60)
print(f'Test A (Sphere->Box):     contacts={steps_A}, max_pen={pen_A:.6f}')
print(f'Test B (Box->Box):        contacts={steps_B}, max_pen={pen_B:.6f}')
print(f'Test C (Slope->Block):    contacts={steps_C}, max_pen={pen_C:.6f}')
if steps_A > 0 or steps_B > 0 or steps_C > 0:
    print('RESULT: AT LEAST ONE TEST PASSED')
else:
    print('RESULT: ALL TESTS FAILED - no contacts detected')

results = {
    'test_A_contacts': steps_A, 'test_A_max_pen': pen_A,
    'test_B_contacts': steps_B, 'test_B_max_pen': pen_B,
    'test_C_contacts': steps_C, 'test_C_max_pen': pen_C,
}
with open(os.path.join(OUTPUT_DIR, 'collision_minimal_results.json'), 'w') as f:
    json.dump(results, f, indent=2)
