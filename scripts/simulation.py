#!/usr/bin/env python3
import json, csv, os, sys
import numpy as np
sys.path.insert(0, '/root/private_data/chrono/build-py311/bin')
import pychrono as chrono

CONFIG_PATH = '/root/private_data/glacier_fall/config/parameters.json'
OUTPUT_DIR = '/root/private_data/glacier_fall/output'
LOG_DIR = '/root/private_data/glacier_fall/logs'
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

def log(msg):
    print(msg, flush=True)

def _set_slope_rotation(angle):
    m = chrono.ChMatrix33d()
    m.SetFromCardanAnglesZYX(chrono.ChVector3d(0.0, angle, 0.0))
    return m

def analytical_baseline(cfg):
    g = cfg['gravity']
    theta = np.radians(cfg['slope_angle'])
    mu = cfg['friction']
    m = cfg['mass']
    h = cfg['height']
    d = cfg['slope_length']
    a = g * (np.sin(theta) - mu * np.cos(theta))
    t_slope = np.sqrt(2 * d / a) if a > 0 else float('inf')
    v_impact = np.sqrt(2 * a * d)
    mgh = m * g * h
    friction_work = mu * m * g * np.cos(theta) * d
    ke_impact = 0.5 * m * v_impact**2
    log(f'[Analytical] a = {a:.4f} m/s^2')
    log(f'[Analytical] t_slope = {t_slope:.4f} s')
    log(f'[Analytical] v_impact = {v_impact:.4f} m/s')
    log(f'[Analytical] mgh = {mgh:.2f} J')
    log(f'[Analytical] friction_work = {friction_work:.2f} J')
    log(f'[Analytical] KE_impact = {ke_impact:.2f} J')
    return {'a': a, 't_slope': t_slope, 'v_impact': v_impact, 'mgh': mgh, 'friction_work': friction_work, 'ke_impact': ke_impact}

def run_simulation(cfg):
    log('[Sim] Creating ChSystemNSC...')
    sys = chrono.ChSystemNSC()
    sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -cfg['gravity'], 0))
    sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    # NOTE: Do NOT call cs.Initialize() - it breaks contact detection in this binding
    mat = chrono.ChContactMaterialNSC()
    mat.SetFriction(cfg['friction'])
    mat.SetRestitution(cfg['restitution'])
    slope_len = cfg['slope_length']
    theta = np.radians(cfg['slope_angle'])
    slope_body = chrono.ChBodyEasyBox(slope_len + 4.0, 1.0, 4.0, 1000.0, True, True, mat)
    slope_body.SetPos(chrono.ChVector3d(slope_len / 2.0, 0.0, 0.0))
    slope_body.SetRot(_set_slope_rotation(-theta))
    slope_body.SetFixed(True)
    sys.AddBody(slope_body)
    block = chrono.ChBodyEasyBox(2.0, 1.0, 2.0, cfg['mass'], True, True, mat)
    block.SetPos(chrono.ChVector3d(0.0, cfg['height'], 0.0))
    block.SetLinVel(chrono.ChVector3d(0.0, 0.0, 0.0))
    sys.AddBody(block)
    obs = chrono.ChBodyEasyBox(3.0, 2.0, 3.0, 1000.0, True, True, mat)
    obs.SetPos(chrono.ChVector3d(cfg['obstacle_x'], cfg['obstacle_y'], 0.0))
    obs.SetFixed(True)
    sys.AddBody(obs)
    log(f'[Sim] Block initial pos: ({block.GetPos().x:.2f}, {block.GetPos().y:.2f})')
    log(f'[Sim] Obstacle pos: ({obs.GetPos().x:.2f}, {obs.GetPos().y:.2f})')
    dt = cfg['dt']
    t = 0.0
    step = 0
    contact_detected = False
    contact_step = -1
    contact_time = -1.0
    max_contacts = 0
    csv_path = os.path.join(OUTPUT_DIR, 'time_series.csv')
    csv_file = open(csv_path, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['step', 'time', 'block_x', 'block_y', 'block_z', 'block_vx', 'block_vy', 'block_vz', 'contacts', 'fx', 'fy', 'fz'])
    log('[Sim] Starting time stepping...')
    while t < cfg['t_max'] and step < 2000000:
        sys.DoStepDynamics(dt)
        t += dt
        step += 1
        if step % 10000 == 0:
            n_contacts = sys.GetContactContainer().GetNumContacts()
            max_contacts = max(max_contacts, n_contacts)
            if n_contacts > 0 and not contact_detected:
                contact_detected = True
                contact_step = step
                contact_time = t
                log(f'[Sim] CONTACT at t={t:.4f}s, step={step}, y={block.GetPos().y:.4f}')
            log(f'[Sim] step={step}, t={t:.4f}, y={block.GetPos().y:.4f}, vy={block.GetLinVel().y:.4f}, contacts={n_contacts}')
        if step % 1000 == 0:
            n_contacts = sys.GetContactContainer().GetNumContacts()
            fx, fy, fz = 0.0, 0.0, 0.0
            if n_contacts > 0:
                try:
                    c = sys.GetContactContainer().GetContact(0)
                    if c:
                        force = c.GetContactableForce()
                        fx, fy, fz = force.x, force.y, force.z
                except Exception:
                    pass
            csv_writer.writerow([step, f'{t:.6f}', f'{block.GetPos().x:.6f}', f'{block.GetPos().y:.6f}', f'{block.GetPos().z:.6f}', f'{block.GetLinVel().x:.6f}', f'{block.GetLinVel().y:.6f}', f'{block.GetLinVel().z:.6f}', n_contacts, f'{fx:.4f}', f'{fy:.4f}', f'{fz:.4f}'])
    csv_file.close()
    log(f'[Sim] Final: t={t:.4f}s, y={block.GetPos().y:.4f}, vy={block.GetLinVel().y:.4f}')
    log(f'[Sim] Contact detected: {contact_detected} at t={contact_time:.4f}s')
    log(f'[Sim] Max contacts: {max_contacts}')
    result = {'final_time': t, 'final_y': float(block.GetPos().y), 'final_vy': float(block.GetLinVel().y), 'final_vx': float(block.GetLinVel().x), 'contact_detected': contact_detected, 'contact_time': contact_time, 'contact_step': contact_step, 'max_contacts': max_contacts}
    with open(os.path.join(OUTPUT_DIR, 'result.json'), 'w') as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == '__main__':
    log('=' * 60)
    log('Glacier Ice-Rock Fall Simulation')
    log('=' * 60)
    log(f'[Config] {json.dumps(CONFIG, indent=2)}')
    log('\n[Analytical] Computing baseline...')
    baseline = analytical_baseline(CONFIG)
    with open(os.path.join(OUTPUT_DIR, 'analytical_baseline.json'), 'w') as f:
        json.dump(baseline, f, indent=2)
    log('\n[Sim] Running PyChrono simulation...')
    result = run_simulation(CONFIG)
    log('\n[DONE] Output in /root/private_data/glacier_fall/output/')
