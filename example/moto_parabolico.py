import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from general import *

def main():
    pygame.init()
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    timekeeper = TimeKeeper()
    timekeeper.start()
    
    entities = [Entity(x=300, y=screen_height, mass=10)]
    world = World(dimX=screen.get_size()[0], dimY=screen.get_size()[1], entities=entities)
    
    esplosione = Force(magnitude=900, alpha=math.radians(45))
    gravity = Force(magnitude=(entities[0].mass * World.gravAcc), alpha=math.radians(270))
    
    # non sto considerando la resistenza dell'aria e molte altre forze quindi il proiettile non perderà mai velocità orrizzontale
    entities[0].addForce(gravity, name="gravity", duration=0)
    entities[0].addForce(esplosione, name="sparo", duration=1)
    
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
        
        for entity in entities:
            entity.update(delta_time, (screen_width, screen_height))
        
        screen.fill((0, 0, 0))
        world.render(screen)
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()