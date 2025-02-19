from env import *

mike = Entity("cube", dimensions=(0.5, 0.5, 0.5), position=(2, 1))

world = World(dimensions=(75, 100))
world.addEntity(mike)
world.setGravity(True)
world.start()