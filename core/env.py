import pygame
import time
import threading
import math

class World:
    gravAcc = 9.81
    METERS_TO_PIXELS = None  # pixel per metro
    
    def __init__(self, meters=5000):
        pygame.init()
        
        screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
        self.timekeeper = TimeKeeper()
        
        self.dimX = screen_width
        self.dimY = screen_height
        World.METERS_TO_PIXELS = screen_width / meters  # 1000 metri = larghezza schermo
        self.world = [[0 for _ in range(screen_width)] for _ in range(screen_height)]
        
    def start(self):
        self.timekeeper.start()
    
        running = True
        while running:
            delta_time = self.timekeeper.delta_time
            self.timekeeper.delta_time = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update(delta_time)
            self.render(self.screen)
            
            pygame.display.flip()
            
            self.clock.tick(60)

        pygame.quit()

    def set_entities(self, entities):
        self.entities = entities
        
    def setGravity(self, active=True):
        if active:
            for entity in self.entities:
                gravity = Force(magnitude=(entity.mass * self.gravAcc), alpha=math.radians(270), name="gravity")
                entity.addForce(gravity, duration=0)
    
    def setAirDrag(self, active=True):
        self.airDragActive = active
        self.airDragForce = AirDrag()
        
    def update(self, delta_time):
        for entity in self.entities:
            entity.update(delta_time, (self.dimX, self.dimY))
            
            if self.airDragActive:
                self.airDragForce.update(entity)
        
    def render(self, screen):
        screen.fill((0, 0, 0))
        for entity in self.entities:
            # Converti le coordinate da metri a pixel
            pixel_x = entity.x * World.METERS_TO_PIXELS
            pixel_y = entity.y * World.METERS_TO_PIXELS
            pygame.draw.circle(screen, (255, 0, 0), (pixel_x, pixel_y), 5)

        
class Entity:        
    def __init__(self, x=250, y=250, mass=0, drag_coefficient=0, trasversal_area=0, world=None):
        # x e y ora sono in metri
        self.x = x / World.METERS_TO_PIXELS if World.METERS_TO_PIXELS else x
        self.y = (world.dimY -  y) / World.METERS_TO_PIXELS if World.METERS_TO_PIXELS else y
        self.mass = mass
        self.velocity_x = 0 
        self.velocity_y = 0
        self.drag_coefficient = drag_coefficient
        self.trasversal_area = trasversal_area
        self.forces = []
    
    def addForce(self, force, duration=0):
        if duration > 0:
            force.start_time = time.time()
            force.duration = duration
        else:
            force.start_time = 0
            force.duration = float('inf')
            
        for f in self.forces:
            if f.name == force.name:
                self.forces.remove(f)
        self.forces.append(force)
    
    def update(self, delta_time, bounds):
        current_time = time.time()
        self.forces = [f for f in self.forces if (current_time - f.start_time) < f.duration]
        
        total_force_x = 0
        total_force_y = 0
        
        for force in self.forces:
            total_force_x += force.magnitude * math.cos(force.alpha)
            total_force_y += force.magnitude * math.sin(force.alpha)
        
        # Calcoliamo l'accelerazione (F = m * a => a = F/m)
        acceleration_x = total_force_x / self.mass if self.mass != 0 else 0
        acceleration_y = total_force_y / self.mass if self.mass != 0 else 0

        # Calcoliamo la velocità (v = u + at)
        self.velocity_x += acceleration_x * delta_time
        self.velocity_y += acceleration_y * delta_time
        
        self.alpha = math.fabs(math.degrees(math.atan2(self.velocity_y, self.velocity_x)))

        # Aggiorniamo la posizione (x = x0 + vt) - ora in metri
        self.x += (self.velocity_x * delta_time)
        self.y += (self.velocity_y * delta_time)
        
        # Converti i bounds da pixel a metri per il controllo
        bounds_meters = (bounds[0] / World.METERS_TO_PIXELS, bounds[1] / World.METERS_TO_PIXELS)
        self.x = max(0, min(self.x, bounds_meters[0]))
        self.y = max(0, min(self.y, bounds_meters[1]))

        print(f"Entity position: x = {self.x:.2f}m, y = {self.y:.2f}m, velocity_x = {self.velocity_x:.2f}m/s, velocity_y = {self.velocity_y:.2f}m/s")


class Force:
    def __init__(self, magnitude=0, alpha=0, name="general"):
        self.magnitude = magnitude  # Modulo
        self.alpha = -alpha  # segno - perchè viene fatta prima una conversione in radianti che inverte la nostra concezione di angoli (90° in radianti è verso il basso mentre noi 90° lo vediamo verso l'alto)
        self.name = name
        
        
class AirDrag(Force):
    def __init__(self, air_density=1.225):
        self.air_density = air_density
    
    def update(self, entity):
        self.velocity = math.sqrt(entity.velocity_x**2 + entity.velocity_y**2)
        self.magnitude = 0.5 * entity.drag_coefficient * self.air_density * entity.trasversal_area * self.velocity**2
        self.alpha = (entity.alpha + 180) % 360
        
        drag = Force(magnitude=self.magnitude, alpha=math.radians(self.alpha), name="air_drag")
        entity.addForce(drag, duration=0)
        
        print(f"Air drag force: magnitude = {self.magnitude:.2f}N, alpha = {self.alpha:.2f}° \n")
        
class TimeKeeper:
    def __init__(self):
        self.current_time = 0
        self.last_time = time.time()
        self.delta_time = 0
        self.running = True
        self.thread = threading.Thread(target=self.update_time)
        self.thread.daemon = True

    def update_time(self):
        while self.running:
            current = time.time()
            self.delta_time = current - self.last_time
            self.last_time = current
            self.current_time += self.delta_time
            time.sleep(0.001)
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()