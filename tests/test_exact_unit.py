import pychrono as chrono

mat = chrono.ChContactMaterialNSC()
mat.SetFriction(0.3)
mat.SetRestitution(0.5)
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
cs = sys.GetCollisionSystem()
if cs:
    cs.Initialize()
sphere = chrono.ChBody()
sphere.SetMass(500.0)
sphere.SetInertiaXX(chrono.ChVector3d(1,1,1) * 0.4 * 500.0 * 0.5**2)
sphere.SetPos(chrono.ChVector3d(0.0, 0.0, 1.0))
sphere.SetRot(chrono.ChQuaterniond(1,0,0,0))
sphere.SetPosDt(chrono.ChVector3d(0,0,0))
sphere.SetAngVelParent(chrono.ChVector3d(0,0,0))
sphere.EnableCollision(True)
sphere.SetFixed(False)
sphere.AddCollisionShape(chrono.ChCollisionShapeSphere(mat, 0.5))
box = chrono.CreateBoxContainer(sys, mat, chrono.ChVector3d(4.0, 4.0, 4.0), 0.1)
sys.AddBody(sphere)
sys.AddBody(box)
print('Contacts after AddBody:', sys.GetContactContainer().GetNumContacts())
for i in range(200):
    sys.DoStepDynamics(5e-3)
    n = sys.GetContactContainer().GetNumContacts()
    if n > 0:
        print(f'Step {i}, contacts={n}, sphere z={sphere.GetPos().z:.4f}')
        break
print('Final contacts:', sys.GetContactContainer().GetNumContacts())
print('Sphere pos:', sphere.GetPos().z)
