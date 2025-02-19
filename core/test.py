from coreV2 import *

mike = Entity("cube", dimensions=(1, 1, 1), position=(2, 1))

world = World(dimensions=(75, 100))
world.addEntity(mike)
world.setGravity(True)
world.setAirDrag(True)

newForce = Force(magnitude=5, direction=0, name="newForce", duration=1)
mike.addForce(newForce)

world.start()