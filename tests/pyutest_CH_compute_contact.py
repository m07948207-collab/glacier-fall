import pychrono as chrono

gravity = -9.81
system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, gravity))

friction = 0.4
restitution = 0
mat = chrono.ChContactMaterialNSC()
mat.SetRestitution(restitution)
mat.SetFriction(friction)

num_balls = 8
radius = 0.05
mass = 5.0
pos = chrono.ChVector3d(0, 0, 0.06)
rot = chrono.ChQuaterniond(1, 0, 0, 0)
init_vel = chrono.ChVector3d(0, 0, 0)
init_omg = chrono.ChVector3d(0, 0, 0)

balls = []
for i in range(num_balls):
    ball = chrono.ChBody()
    ball.SetMass(mass)
    ball.SetInertiaXX(chrono.ChVector3d(1, 1, 1) * 0.4 * mass * radius * radius)
    ball.SetPos(pos + chrono.ChVector3d(i * 2 * radius, i * 2 * radius, 0))
    ball.SetRot(rot)
    ball.SetPosDt(init_vel)
    ball.SetAngVelParent(init_omg)
    ball.EnableCollision(True)
    ball.SetFixed(False)
    ct_shape = chrono.ChCollisionShapeSphere(mat, radius)
    ball.AddCollisionShape(ct_shape)
    system.AddBody(ball)
    balls.append(ball)

bin_width = 20.0
bin_length = 20.0
bin_thickness = 0.1
ground = chrono.CreateBoxContainer(system, mat, chrono.ChVector3d(bin_width, bin_length, 2 * radius), bin_thickness)

print('Balls created:', len(balls))
print('Ground created:', ground)
print('Initial contacts:', system.GetContactContainer().GetNumContacts())

end_time = 1.0
time_step = 5e-3
while system.GetChTime() < end_time:
    system.DoStepDynamics(time_step)
    n = system.GetContactContainer().GetNumContacts()
    if n > 0:
        print(f't={system.GetChTime():.4f}, contacts={n}')
        break

final_contacts = system.GetContactContainer().GetNumContacts()
print('Final contacts:', final_contacts)
print('Ball0 pos:', balls[0].GetPos().z)
