import pychrono as chrono
s = chrono.ChSystemNSC()
print('Solver methods:', [m for m in dir(s) if 'solver' in m.lower()])
print('Solver type:', s.GetSolverType())
print('MaxPenRecovery:', [m for m in dir(s) if 'penetration' in m.lower()])
try:
    print('SetMaxPenetrationRecoverySpeed exists:', hasattr(s, 'SetMaxPenetrationRecoverySpeed'))
except Exception as e:
    print('Error:', e)
try:
    s.SetMaxPenetrationRecoverySpeed(0.5)
    print('SetMaxPenetrationRecoverySpeed(0.5) OK')
except Exception as e:
    print('SetMaxPenetrationRecoverySpeed failed:', e)
try:
    s.SetSolverType(chrono.ChSolver.Type_NSC)
    print('SetSolverType NSC OK')
except Exception as e:
    print('SetSolverType failed:', e)
