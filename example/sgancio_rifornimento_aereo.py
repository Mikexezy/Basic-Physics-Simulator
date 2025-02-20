import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env import *

world = World(meters=10000)
entities = [Entity(x=(10 * World.METERS_TO_PIXELS), y=(8000 * World.METERS_TO_PIXELS), mass=2, trasversal_area=0.2, drag_coefficient=0.1, world=world)]
    
world.set_entities(entities)
world.setGravity(True)
world.setAirDrag(True)
    
entities[0].velocity_x = 200

world.start()