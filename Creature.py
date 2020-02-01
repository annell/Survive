from Common import Direction
from Common import Physics 
from Common import Screen
from Common import Biome
import pygame
import random


class Creature():
    def __init__(self, x, y, width, height, color, speed):
        self.hitbox = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dx = 0
        self.dy = 0
        self.speed = speed
        self.onGround = False
        self.color = color
        self.inWater = False
    
    def Step(self):
        pass

    def Move(self, direction, keyHold):
        if keyHold:
            if direction == Direction.RIGHT:
                self.dx = self.speed
            elif direction == Direction.LEFT:
                self.dx = -self.speed
            elif direction == Direction.UP:
                if self.onGround:
                    self.dy = Physics.JUMPHEIGHT
                elif self.inWater:
                    self.dy = Physics.JUMPHEIGHT
            elif direction == Direction.DOWN:
                if self.inWater:
                    self.dy = -Physics.JUMPHEIGHT
        else:
            if direction == Direction.RIGHT:
                self.dx = 0
            elif direction == Direction.LEFT:
                self.dx = 0
    
    def Falling(self):
        self.dy += Physics.GRAVITY / Physics.FPS
        if self.dy > Physics.MAXVSPEED:
            self.dy = Physics.MAXVSPEED
        self.onGround = False
    
    def OnGround(self):
        self.onGround = True
        self.dy = 0
    
    def HitWall(self):
        pass
    
    def HitRoof(self):
        self.dy = -self.dy/2
    
    def InWater(self):
        self.inWater = True
        self.onGround = False
    
    def Entity(self):
        return self.color, self.hitbox
    
    def GetPosition(self):
        return self.x, self.y

class AiControlled(Creature):
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height, color, speed)
        self.goal = self.GetNewGoal()
        self.againstWall = False
    
    def HitWall(self):
        self.againstWall = True
    
    def Wander(self):
        pass
    
    def Flee(self):
        pass
    
    def Seek(self, goal):
        distance = goal - self.x
        if distance < 0:
            self.Move(Direction.LEFT, True)
        else:
            self.Move(Direction.RIGHT, True)
        return abs(distance) < 10
    
    def Step(self):
        if self.againstWall:
            self.Move(Direction.UP, True)
            self.againstWall = False
        if self.inWater:
            self.Move(Direction.UP, True)
        if self.Seek(self.goal):
            self.goal = self.GetNewGoal()
    
    def GetNewGoal(self):
        goaldistance = random.randrange(-300, 300)
        return self.x + goaldistance

class Player(Creature):
    def __init__(self, x, y):
        width = 15
        height = 35
        color = (255, 0, 255)
        speed = 2
        super().__init__(x, y, width, height, color, speed)
        self.selectedBlock = False
        self.mouseDirection = (0, 0)
    
    def SelectBlock(self, block, direction):
        self.selectedBlock = block
        dx0, dy0 = direction
        dx = self.x + dx0*100/(abs(dx0) + abs(dy0))
        dy = self.y + dy0*100/(abs(dx0) + abs(dy0))
        self.mouseDirection = (dx, dy)
        if block:
            block.highlighted = True
    
    def Action(self, world):
        if self.selectedBlock and not self.selectedBlock.color == Biome.WATER:
            world.DeleteBlock(self.selectedBlock)

class Pigg(AiControlled):
    def __init__(self, x, y):
        width = 35
        height = 20
        color = (255, 128, 192)
        speed = 0.75
        super().__init__(x, y, width, height, color, speed)

class Sheep(AiControlled):
    def __init__(self, x, y):
        width = 30
        height = 18
        color = (255, 255, 255)
        speed = 0.8
        super().__init__(x, y, width, height, color, speed)

class Zombie(AiControlled):
    def __init__(self, x, y):
        width = 18
        height = 30
        color = (4, 120, 0)
        speed = 1
        super().__init__(x, y, width, height, color, speed)