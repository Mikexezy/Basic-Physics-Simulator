from coreV2 import *

world = World(dimensions=(75, 100))

plane = Entity("plane", dimensions=(75, 10, 1), position=(0, 90), alpha=5)
plane2 = Entity("plane", dimensions=(100, 30, 1), position=(10, 90), alpha=90)

mike = Entity("cube", dimensions=(5, 5, 5), position=(10, 10), mass=10)
world.addEntity(plane)
world.addEntity(plane2)
world.addEntity(mike)

world.setCollision(mike, plane)
world.setCollision(mike, plane2)


world.setGravity(True)
world.setAirDrag(True)

world.start()               