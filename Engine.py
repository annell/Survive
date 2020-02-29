import pygame
import random
import math

from Common import Physics
from Common import BlockType
from Common import Screen 

from Creature import Pigg
from Creature import Zombie
from Creature import Sheep


class Engine():
    def __init__(self, displaySurf, camera, enviroment):
        self.camera = camera
        self.enviroment = enviroment
        self._display_surf = displaySurf
        self.lightSources = []
        self.renderedBlocks = []
    
    def CollisionCheck(self, objects):
        for obj in objects:
            obj.inWater = False
            obj.Falling()
            blocks = self.enviroment.BlocksAt((obj.x + obj.width/2, obj.y + obj.height/2), max([obj.height,obj.width]))
            self.MoveSingleAxis(obj, blocks, obj.dx, 0)
            self.MoveSingleAxis(obj, blocks, 0, obj.dy)
    
    def MoveSingleAxis(self, obj, blocks, dx, dy):
        obj.x += dx
        obj.y += dy
        hitbox = pygame.Rect(obj.x, math.ceil(obj.y), obj.width, obj.height)
        for block in blocks:
            if hitbox.colliderect(block.hitboxWorldFrame):
                if block.color == BlockType.WATER:
                    obj.InWater()
                else:
                    if dx > 0:
                        obj.x = block.hitboxWorldFrame.left - obj.width
                        obj.HitWall()
                    if dx < 0:
                        obj.x = block.hitboxWorldFrame.right
                        obj.HitWall()
                    if dy > 0:
                        obj.y = block.hitboxWorldFrame.top - obj.height
                        obj.OnGround()
                    if dy < 0:
                        obj.y = block.hitboxWorldFrame.bottom
                        obj.HitRoof()
                    break
    
    def ClosestIntersectingBlock(self, ray, distance, ignoreBlock=None):
        dx0 = ray[0][0] - ray[1][0]
        dy0 = ray[0][1] - ray[1][1]
        x0 = ray[0][0]
        y0 = ray[0][1]
        stepsize = 20
        dx = dx0/(abs(dx0) + abs(dy0))
        dy = dy0/(abs(dx0) + abs(dy0))
        x = x0
        y = y0
        for _ in range(0, distance):
            x -= dx * stepsize
            y -= dy * stepsize
            if math.hypot(x - x0, y - y0) > distance:
                return None
            block = self.BlockAt(self.camera.WorldToBlockgrid((x, y)))
            if block:
                if ignoreBlock == block:
                    return None
                return block

    def RenderBlocks(self):
        self.camera.PlaceInScene(self.renderedBlocks)
        for block in self.renderedBlocks:
            if block.render:
                if block.highlighted:
                    pygame.draw.rect(self._display_surf, (255, 0, 0), block.hitbox)
                    block.highlighted = False
                else:
                    pygame.draw.rect(self._display_surf, block.color, block.hitbox)
            block.render -= 1
            if not block.render:
                self.renderedBlocks.remove(block)
    
    def SpawnCreatures(self, player, creatures):
        for creature in creatures:
            if abs(player.x - creature.x) > Physics.SPAWNDISTANCE:
                creatures.remove(creature)
        for _ in range(Physics.NRCREATURES - len(creatures)):
            r = random.random()
            x = random.randrange(-Physics.SPAWNDISTANCE, Physics.SPAWNDISTANCE)
            y = self.enviroment.GetTopLayerCoordinate(int(x/Physics.BLOCKWIDTH)) - 1
            y *= Physics.BLOCKHEIGHT
            creature = None
            if r < 0.05:
                creature = Zombie(x, y)
            elif r < 0.4:
                creature = Sheep(x, y)
            else:
                creature = Pigg(x, y)
            creatures.append(creature)

    def AddLight(self, block):
        self.lightSources.append(block)

    def LightSource(self):
        maxRays = 100
        for light in self.lightSources:
            light.render = 200
            nrRays = int(maxRays/len(self.lightSources))
            x, y = light.x, light.y 
            x += Physics.BLOCKWIDTH/2
            y += Physics.BLOCKHEIGHT/2
            for _ in range(nrRays):
                angle = random.random()*2*math.pi
                dx = math.cos(angle)
                dy = math.sin(angle)
                rx = x + dx
                ry = y + dy
                block = self.ClosestIntersectingBlock(((x, y), (rx, ry)), Screen.RAYDISTANCE, ignoreBlock=light)
                if block:
                    block.render = 100
                    if block not in self.renderedBlocks:
                        self.renderedBlocks.append(block)
    
    def CreateBlock(self, pos, blockType):
        x, y = self.camera.WorldToBlockgrid(pos)
        if self.BlockAt((x, y)):
            return False
        block = self.enviroment.CreateBlock((x, y), blockType)
        if block.color == BlockType.LIGHT:
            self.AddLight(block)
        return block
    
    def DeleteBlock(self, block):
        self.renderedBlocks.remove(block)
        if block.color == BlockType.LIGHT:
            self.lightSources.remove(block)
        self.enviroment.DeleteBlock(block)
    
    def BlockAt(self, pos):
        return self.enviroment.BlockAt(pos)
