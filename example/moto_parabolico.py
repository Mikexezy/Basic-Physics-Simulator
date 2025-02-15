import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env import *

world = World(meters=100)
entities = [Entity(x=(10 * World.METERS_TO_PIXELS), y=(1 * World.METERS_TO_PIXELS), mass=2, trasversal_area=0.1, drag_coefficient=2, world=world)]
    
world.set_entities(entities)
world.setGravity(True)
world.setAirDrag(True)
    
esplosione = Force(magnitude=2000, alpha=math.radians(25), name="sparo")
    
entities[0].addForce(esplosione, duration=0.05)
    
world.start()