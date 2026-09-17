#!/usr/bin/env python3
import pychrono as chrono
sys = chrono.ChSystemNSC()
methods = [m for m in dir(sys) if any(x in m.lower() for x in ['solver', 'iter', 'max', 'tol', 'residual', 'contact', 'collision'])]
print('ChSystemNSC methods:', methods[:40])
