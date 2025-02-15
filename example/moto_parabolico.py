import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env import *

def main():
    pygame.init()
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    timekeeper = TimeKeeper()
    
    world = World(dimX=screen.get_size()[0], dimY=screen.get_size()[1], meters=100)
    entities = [Entity(x=(10 * World.METERS_TO_PIXELS), y=(screen.get_size()[1] - (1 * World.METERS_TO_PIXELS)), mass=2, trasversal_area=0.1, drag_coefficient=2)]
    
    world.set_entities(entities)
    world.setGravity(True)
    world.setAirDrag(True)
    
    esplosione = Force(magnitude=2000, alpha=math.radians(25), name="sparo")
    
    # non sto considerando la resistenza dell'aria e molte altre forze quindi il proiettile non perderà mai velocità orrizzontale
    entities[0].addForce(esplosione, duration=0.05)
    
    timekeeper.start()
    
    running = True
    while running:
        delta_time = timekeeper.delta_time
        timekeeper.delta_time = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        world.update(delta_time)
        world.render(screen)
        
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()