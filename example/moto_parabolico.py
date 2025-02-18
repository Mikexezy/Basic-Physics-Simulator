import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env import *

world = World(meters=10)
entities = [Entity(x=(0.5 * World.METERS_TO_PIXELS), y=(1 * World.METERS_TO_PIXELS), mass=2, trasversal_area=0.25, drag_coefficient=1, world=world)]
    
world.set_entities(entities)
world.setGravity(True)
world.setAirDrag(True)
    
lancio = Force(magnitude=200, alpha=math.radians(25), name="sparo")
    
entities[0].addForce(lancio, duration=0.1)
    
world.start()