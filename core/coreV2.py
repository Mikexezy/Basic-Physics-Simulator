import pygame
import time
import threading
import math

#TODO: rifare tutto con più ordine

# topology - "cube", "parallelepiped", "sphere", "plane"

class Timer:
    def __init__(self):
        self.last_time = time.time()
        self.first_time = self.last_time
    
    
    def getDeltaTime(self):
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time
        
        return delta
        
    
class World:
    GRAV = 9.81
    
    
    def __init__(self, dimensions=(20, 15), title="Pernaci Engine"):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        self.title = pygame.display.set_caption(title)
        
        self.dimensions = dimensions
        self.PTM = ((self.screen.get_width() / dimensions[0]), (self.screen.get_height() / dimensions[1]))
        
        self.entities = []
        
        self.timer = Timer()
        
        
    def addEntity(self, entity):
        self.entities.append(entity)
        
        
    def setGravity(self, active=True):
        if active:
            for entity in self.entities:
                gravity = Force(magnitude=entity.weightForce, direction=270, name="gravity")
                entity.addForce(gravity)
    
                
    def setAirDrag(self, active=True):
        self.airdrag = active
        
        if active:
            for entity in self.entities:
                airDragCalculator = threading.Thread(target=calculateAirDrag, args=(entity,))
                entity.threads.append([airDragCalculator, "airdrag"])
                
                for thread, name in entity.threads:
                    if name == "airdrag":
                        thread.daemon = True
                        thread.start() 


    def render(self):
        self.screen.fill((0, 0, 0))
        for entity in self.entities:
            if entity.topology == "sphere":
                pygame.draw.circle(self.screen, (255, 0, 0), (entity.position[0] * self.PTM[0], entity.position[1] * self.PTM[1]), entity.dimensions[2])
            elif entity.topology == "plane":
                pygame.draw.rect(self.screen, (255, 255, 255), (entity.position[0] * self.PTM[0], entity.position[1] * self.PTM[1], entity.dimensions[0] * self.PTM[0], entity.dimensions[1] * self.PTM[1]))
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), (entity.position[0] * self.PTM[0], entity.position[1] * self.PTM[1], entity.dimensions[0] * self.PTM[0], entity.dimensions[1] * self.PTM[1]))
                
    def start(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        
            for entity in self.entities:
                entity.calculateForce(self)
                print("Position: ", entity.position)
                print("Velocity: ", entity.velX, entity.velY)
                print("Forces: ", entity.forces)
                print("\n")
                
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
            
        
        
class Entity:
    #l'unità di misura per la lunghezza => Metro
    
    # dimensions = larghezza, altezza, lunghezza o raggio
    # position = x da sinistra, y dal basso
    
    def __init__(self, topology="cube", dimensions=(1,1,1), mass=1, drag_coefficient=0.1, position=(10, 10)):
        self.topology = topology
        self.dimensions = dimensions
        
        if self.topology == "plane":
            self.mass = None
            self.weightForce = None
            self.volume = None
            self.density = None
            self.velX = None
            self.velY = None
            self.direction = None
            self.drag_coefficient = None
            self.trasversal_area = None
        else:
            self.mass = mass
            self.weightForce = self.mass * World.GRAV
            self.volume = getVolume(self.topology, self.dimensions)
            self.density = self.mass / self.volume
            self.velX = 0
            self.velY = 0   
            self.direction = math.atan2(self.velY, self.velX)
            self.drag_coefficient = drag_coefficient
            self.trasversal_area = getArea(self.topology, self.dimensions)
            
        self.position = position 
        self.forces = []
             
        self.threads = []
        
        
    def addForce(self, force):
        for f in self.forces:
            
            if f.name == force.name: 
                self.forces.remove(f)
        
        self.forces.append(force)
            
    def calculateForce(self, world):
        if self.topology == "plane":
            return
        
        # Calcola la forza totale
        total_fx = 0
        total_fy = 0
        
        for force in self.forces:
            if (time.time() - world.timer.first_time) > force.duration:
                self.forces.remove(force)
                continue
            
            fx, fy = force.getComponents()
            total_fx += fx
            total_fy += fy
        
        # F = ma => a = F/m
        acceleration_x = total_fx / self.mass
        acceleration_y = total_fy / self.mass
        
        delta_time = world.timer.getDeltaTime()
        
        # v = v0 + at
        self.velX = self.velX + (acceleration_x * delta_time)
        self.velY = self.velY + (acceleration_y * delta_time)
        
        # x = x0 + vt + (1/2)at²
        delta_x = (self.velX * delta_time) + (0.5 * acceleration_x * delta_time * delta_time)
        delta_y = (self.velY * delta_time) + (0.5 * acceleration_y * delta_time * delta_time)
        
        # Converti lo spostamento in pixel
        motion_x = delta_x * world.PTM[0]
        motion_y = delta_y * world.PTM[1]
        
        # Aggiorna la posizione (nota: y è invertito in pygame)
        self.position = (
            self.position[0] + motion_x, 
            self.position[1] - motion_y  # Il segno - perché l'asse y è invertito in pygame
        )
                            
        
        
class Force:
    def __init__(self, magnitude=100, direction=0, duration=0, name="general"):
        self.magnitude = magnitude
        self.direction = direction
        self.radiants = math.radians(direction)
        self.name = name
        
        if duration == 0:
            self.duration = float("inf")
        else:
            self.duration = duration
        
        
        
    def getComponents(self):
        fx = self.magnitude * math.cos(self.radiants)
        fy = self.magnitude * math.sin(self.radiants)
        
        return fx, fy
    
    
    
def getArea(topology, dimensions):
    if topology == "plane":
        return
        
    if topology == "cube":
        return dimensions[0] * dimensions[1]
    elif topology == "parallelepiped":
        return (dimensions[0] * dimensions[2]) + (dimensions[0] * dimensions[1]) + (dimensions[1] * dimensions[2])
    elif topology == "sphere":
        return math.pi * dimensions[2]**2
    else:
        print("Invalid topology")
        return 0
        
def getVolume(topology, dimensions):
    if topology == "plane":
        return
        
    if topology == "cube" or topology == "parallelepiped":
        return (dimensions[0] * dimensions[2]) * dimensions[1]
    elif topology == "sphere":
        return (4/3) * math.pi * dimensions[2]**3
    else:
        print("Invalid topology")
        return 0
    
def calculateAirDrag(entity):
    if entity.topology == "plane":
        return
    
    while True:
        if entity.velX == 0 and entity.velY == 0:
            continue
            
        velocity = math.sqrt(entity.velX**2 + entity.velY**2)
        drag_force = 0.5 * 1.225 * velocity**2 * entity.drag_coefficient * entity.trasversal_area
        
        # Calcola l'angolo opposto alla direzione del movimento
        angle = (math.degrees(math.atan2(entity.velY, entity.velX)) + 180) % 360
        
        drag = Force(magnitude=drag_force, direction=angle, name="air_drag")
        entity.addForce(drag)
        
        time.sleep(0.01)  # Aggiorna circa 60 volte al secondo