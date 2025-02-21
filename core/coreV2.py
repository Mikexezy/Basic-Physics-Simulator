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
    worlds = []
    GRAV = 9.81
    
    
    def __init__(self, dimensions=(20, 15), title="Pernaci Engine"):
        self.worlds.append(self)
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        self.title = pygame.display.set_caption(title)
        
        self.dimensions = dimensions
        self.PTM = ((self.screen.get_width() / dimensions[0]), (self.screen.get_height() / dimensions[1]))
        
        self.entities = []
        
        self.possibleCollisions = []
        
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
                        
    
    def setCollision(self, entity1, entity2, name="collision"):
        self.possibleCollisions.append([entity1, entity2, name])
        
    
    def checkCollisions(self):
        while True:
            for entity1, entity2, name in self.possibleCollisions:
                if entity2.topology == "plane":
                    # Calcola il centro del piano
                    plane_center_x = entity2.position[0] * self.PTM[0] + (entity2.dimensions[0] * self.PTM[0] / 2)
                    plane_center_y = entity2.position[1] * self.PTM[1] + (entity2.dimensions[1] * self.PTM[1] / 2)
                    
                    # Calcola i vertici del piano ruotato
                    width = entity2.dimensions[0] * self.PTM[0]
                    height = entity2.dimensions[1] * self.PTM[1]
                    angle = math.radians(entity2.alpha)
                    
                    plane_points = [
                        (-width/2, -height/2),
                        (width/2, -height/2),
                        (width/2, height/2),
                        (-width/2, height/2)
                    ]
                    
                    # Ruota i punti del piano
                    plane_vertices = []
                    for x, y in plane_points:
                        rx = x * math.cos(angle) - y * math.sin(angle)
                        ry = x * math.sin(angle) + y * math.cos(angle)
                        plane_vertices.append((rx + plane_center_x, ry + plane_center_y))
                    
                    # Ottieni i punti dell'entità
                    e1_x = entity1.position[0] * self.PTM[0]
                    e1_y = entity1.position[1] * self.PTM[1]
                    e1_points = [
                        (e1_x, e1_y),
                        (e1_x + entity1.dimensions[0] * self.PTM[0], e1_y),
                        (e1_x + entity1.dimensions[0] * self.PTM[0], e1_y + entity1.dimensions[1] * self.PTM[1]),
                        (e1_x, e1_y + entity1.dimensions[1] * self.PTM[1])
                    ]
                    
                    # Controlla collisione usando il Separating Axis Theorem (SAT)
                    collision = self.checkSATCollision(e1_points, plane_vertices)
                    
                    # Se non c'è collisione, rimuovi le forze vincolari
                    if not collision:
                        entity1.forces = [f for f in entity1.forces if f.name != "vincular"]
                        continue
                    
                    # Se c'è collisione, procedi con il calcolo della forza vincolare
                    if collision:
                        # Calcola la normale del piano (perpendicolare alla superficie)
                        angle = math.radians(entity2.alpha)
                        
                        # Normale che punta verso l'alto del piano
                        plane_normal = (
                            math.sin(angle),
                            math.cos(angle)  # Componente Y invertita
                        )
                        
                        print(f"Debug - Plane normal: ({plane_normal[0]:.2f}, {plane_normal[1]:.2f})")
                        
                        entity1.forces = [f for f in entity1.forces if f.name != "vincular"]
                        
                        # Calcola la forza totale
                        total_fx = 0
                        total_fy = 0
                        for force in entity1.forces:
                            fx, fy = force.getComponents()
                            total_fx += fx
                            total_fy += fy
                        
                        # Proietta la forza sulla normale
                        force_normal = (total_fx * plane_normal[0] + total_fy * plane_normal[1])
                        
                        if force_normal < 0:  # Solo se la forza sta spingendo verso il piano
                            # Rimuovi forze vincolari precedenti
                            
                            # La forza vincolare deve essere nella direzione opposta alla normale
                            vincular_magnitude = abs(force_normal)
                            vincular_direction = -math.degrees(math.atan2(plane_normal[1], plane_normal[0]))
                            
                            vincular_force = Force(
                                magnitude=vincular_magnitude,
                                direction=-vincular_direction,
                                name="vincular"
                            )
                            
                            # Mantieni solo la componente tangenziale della velocità
                            tangent = (-plane_normal[1], plane_normal[0])
                            dot_product = entity1.velX * tangent[0] + entity1.velY * tangent[1]
                            entity1.velX = dot_product * tangent[0] * 0.99  # Aggiungi un po' di attrito
                            entity1.velY = dot_product * tangent[1] * 0.99
                            
                            entity1.addForce(vincular_force)
                            
                            print(f"Debug - Normal: ({plane_normal[0]:.2f}, {plane_normal[1]:.2f})")
                            print(f"Debug - Vincular direction: {vincular_direction:.2f}°")
                            print(f"Debug - Force magnitude: {vincular_magnitude:.2f}")
                
                time.sleep(0.016)

    def checkSATCollision(self, vertices1, vertices2):
        """Implementa il Separating Axis Theorem per la collision detection"""
        for shape in [vertices1, vertices2]:
            for i in range(len(shape)):
                # Calcola la normale dell'edge
                edge = (
                    shape[(i + 1) % len(shape)][0] - shape[i][0],
                    shape[(i + 1) % len(shape)][1] - shape[i][1]
                )
                normal = (-edge[1], edge[0])
                
                # Normalizza
                length = math.sqrt(normal[0]**2 + normal[1]**2)
                normal = (normal[0]/length, normal[1]/length)
                
                # Proietta tutti i punti sulla normale
                min1, max1 = float('inf'), float('-inf')
                min2, max2 = float('inf'), float('-inf')
                
                for vertex in vertices1:
                    projection = vertex[0] * normal[0] + vertex[1] * normal[1]
                    min1 = min(min1, projection)
                    max1 = max(max1, projection)
                
                for vertex in vertices2:
                    projection = vertex[0] * normal[0] + vertex[1] * normal[1]
                    min2 = min(min2, projection)
                    max2 = max(max2, projection)
                
                # Se c'è una separazione, non c'è collisione
                if max1 < min2 or max2 < min1:
                    return False
        
        return True


    def render(self):
        self.screen.fill((0, 0, 0))
        for entity in self.entities:
            if entity.topology == "sphere":
                pygame.draw.circle(self.screen, (255, 0, 0), 
                    (entity.position[0] * self.PTM[0], entity.position[1] * self.PTM[1]), 
                    entity.dimensions[2])
            elif entity.topology == "plane":
                # Calcola il centro del rettangolo
                center_x = entity.position[0] * self.PTM[0] + (entity.dimensions[0] * self.PTM[0] / 2)
                center_y = entity.position[1] * self.PTM[1] + (entity.dimensions[1] * self.PTM[1] / 2)
                
                # Calcola i vertici del rettangolo non ruotato rispetto al centro
                width = entity.dimensions[0] * self.PTM[0]
                height = entity.dimensions[1] * self.PTM[1]
                points = [
                    (-width/2, -height/2),
                    (width/2, -height/2),
                    (width/2, height/2),
                    (-width/2, height/2)
                ]
                
                # Ruota i punti
                angle = math.radians(entity.alpha)
                rotated_points = []
                for x, y in points:
                    # Applica la rotazione
                    rx = x * math.cos(angle) - y * math.sin(angle)
                    ry = x * math.sin(angle) + y * math.cos(angle)
                    # Trasla i punti al centro
                    rotated_points.append((rx + center_x, ry + center_y))
                
                # Disegna il poligono ruotato
                pygame.draw.polygon(self.screen, (255, 255, 255), rotated_points)
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), 
                    (entity.position[0] * self.PTM[0], 
                     entity.position[1] * self.PTM[1], 
                     entity.dimensions[0] * self.PTM[0], 
                     entity.dimensions[1] * self.PTM[1]))
                
                
    def start(self):
        self.collisionChecker = threading.Thread(target=self.checkCollisions)
        self.collisionChecker.daemon = True
        self.collisionChecker.start()
        
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
    
    def __init__(self, topology="cube", dimensions=(1,1,1), mass=1, drag_coefficient=0.1, position=(10, 10), alpha=0):
        self.topology = topology
        self.dimensions = dimensions

        self.mass = mass
        self.weightForce = self.mass * World.GRAV
        self.volume = getVolume(self.topology, self.dimensions)
        self.density = self.mass / self.volume
        
        self.velX = 0
        self.velY = 0   
        
        self.alpha = alpha
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
    if topology == "cube" or topology == "parallelepiped" or topology == "plane":
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