import pygame
import time
import threading
import math

speedOffset = 100  # Offset per la velocità (per rendere più visibile il movimento)

class World:
    gravAcc = 9.81
    
    def __init__(self, dimX, dimY, entities):
        self.dimX = dimX
        self.dimY = dimY
        self.world = [[0 for _ in range(dimX)] for _ in range(dimY)]
        self.entities = entities

    def render(self, screen):
        for entity in self.entities:
            pygame.draw.rect(screen, (255, 0, 0), (entity.x, entity.y, 5, 5))

        
class Entity:        
    def __init__(self, x=250, y=250, mass=0):
        self.x = x
        self.y = y
        self.mass = mass
        self.velocity_x = 0 
        self.velocity_y = 0
        self.forces = []
    
    def addForce(self, force, name="general", duration=0):
        if duration > 0:
            force.start_time = time.time()
            force.duration = duration
        else:
            force.start_time = 0
            force.duration = float('inf')
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

        # Aggiorniamo la posizione (x = x0 + vt)
        self.x += (self.velocity_x * delta_time) * speedOffset
        self.y += (self.velocity_y * delta_time) * speedOffset
        
        # Se esce dalla finestra gli spacco le gambe
        self.x = max(0, min(self.x, bounds[0] - 5))
        self.y = max(0, min(self.y, bounds[1] - 5))

        print(f"Entity position: x = {self.x:.2f}, y = {self.y:.2f}, velocity_x = {self.velocity_x:.2f}, velocity_y = {self.velocity_y:.2f}")


class Force:
    def __init__(self, magnitude=0, alpha=0):
        self.magnitude = magnitude  # Modulo
        self.alpha = -alpha  # segno - perchè viene fatta prima una conversione in radianti che inverte la nostra concezione di angoli (90° in radianti è verso il basso mentre noi 90° lo vediamo verso l'alto)


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