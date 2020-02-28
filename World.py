import pygame
import random
import math
from collections import defaultdict

from Common import Physics
from Common import BlockType
from Common import Screen 

from Creature import Pigg
from Creature import Zombie
from Creature import Sheep

from opensimplex import OpenSimplex
import math

class World():
    def __init__(self, displaySurf, camera):
        self.camera = camera
        self.seed = int(random.random() * 100000.0)
        genHills = OpenSimplex(self.seed)
        genCaves = OpenSimplex(self.seed)
        self.blocks = defaultdict(lambda : {})
        self.renderedBlocks = []
        self.topLayer = defaultdict(lambda : None)
        self.lightSources = []
        self._display_surf = displaySurf
        for x in range(-Physics.MAPWIDTH, Physics.MAPWIDTH):
            height = -5 * self.Noise(0.01 * x, 0, genHills)
            height += -1 * self.Noise(0.06 * x, 0, genHills)
            height += -0.5 * self.Noise(0.12 * x, 0, genHills)
            height = math.pow(height, 3)
            first = True
            for y in range(int(height), Physics.MAPDEPTH):
                if first:
                    if self.GetBlockType(y) == BlockType.WATER:
                        for yn in range(3, y + 1):
                            self.blocks[x][yn] = Block(x*Physics.BLOCKWIDTH, yn*Physics.BLOCKHEIGHT, BlockType.WATER)
                    else:
                        self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, self.GetBlockType(y))

                    self.topLayer[x] = (self.blocks[x][y], y)
                    first = False
                else:
                    if self.topLayer[x][0].color == BlockType.GRASS and abs(y - self.topLayer[x][1]) < 3:
                        self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, BlockType.DIRT)
                    else:
                        self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, BlockType.STONE)

        #Caves
        for x in range(-Physics.MAPWIDTH, Physics.MAPWIDTH):
            if x in self.topLayer:
                for y in range(self.topLayer[x][1], Physics.MAPDEPTH):
                    cave = 1 * self.Noise(0.02 * x, 0.05 * y, genCaves) 
                    if cave < -0.4 and self.blocks[x][y].color != BlockType.WATER:
                        self.blocks[x].pop(y, None)

        #Spread water
        #visited = defaultdict(lambda : defaultdict(lambda : False))
        #for x in range(-Physics.MAPWIDTH, Physics.MAPWIDTH):
        #    for y in range(self.topLayer[x][1], Physics.MAPDEPTH):
        #        if y in self.blocks[x]:
        #            if self.blocks[x][y].color == BlockType.WATER:
        #                self.SpreadWater(x + 1, y, visited)
        #                self.SpreadWater(x - 1, y, visited)
        #                self.SpreadWater(x, y + 1, visited)
        #        visited[x][y] = True
    
    def SpreadWater(self, x, y, visited):
        if visited[x][y]:
            return
        visited[x][y] = True
        if x >= -Physics.MAPWIDTH and x <= Physics.MAPWIDTH and y > -Physics.MAPDEPTH and y < Physics.MAPDEPTH:
            if y not in self.blocks[x]:
                self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, BlockType.WATER)
                self.SpreadWater(x + 1, y, visited)
                self.SpreadWater(x - 1, y, visited)
                self.SpreadWater(x, y + 1, visited)
        
    def GetBlockType(self, y):
        #if y > 2:
        #    return BlockType.WATER
        if y > 0:
            return BlockType.DIRT
        if y > -20:
            return BlockType.GRASS
        if y > -30:
            return BlockType.STONE
        return BlockType.SNOW
    
    def Noise(self, x, y, gen):
        return gen.noise2d(x, y)
    
    def CollisionCheck(self, objects):
        for obj in objects:
            obj.inWater = False
            obj.Falling()
            blocks = self.BlocksAt((obj.x + obj.width/2, obj.y + obj.height/2), max([obj.height,obj.width]))
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
            y = self.GetTopLayerCoordinate(int(x/Physics.BLOCKWIDTH)) - 1
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
    
    def GetTopLayerCoordinate(self, x):
        return self.topLayer[x][1]

    def CreateBlockAt(self, pos, blockType):
        x, y = self.camera.WorldToBlockgrid(pos)
        if self.BlockAt((x, y)):
            return False
        block = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, blockType)
        self.blocks[x][y] = block
        if block.color == BlockType.LIGHT:
            self.AddLight(block)
        return block
    
    def DeleteBlock(self, block):
        self.renderedBlocks.remove(block)
        if block.color == BlockType.LIGHT:
            self.lightSources.remove(block)
        x = (block.hitboxWorldFrame.x) / Physics.BLOCKWIDTH
        y = (block.hitboxWorldFrame.y) / Physics.BLOCKHEIGHT
        self.blocks[x].pop(y, None)
    
    def BlockAt(self, pos):
        x, y = pos
        if x in self.blocks and y in self.blocks[x] and self.blocks[x][y]:
            return self.blocks[x][y]
        return None
        
    def BlocksAt(self, pos, distance=20):
        blocks = []
        x, y = pos
        xBlock = (x) / Physics.BLOCKWIDTH
        yBlock = (y) / Physics.BLOCKHEIGHT
        distanceBlock = distance / Physics.BLOCKWIDTH
        for xPos in range(round(xBlock - distanceBlock), round(xBlock + distanceBlock)):
            for yPos in range(round(yBlock - distanceBlock), round(yBlock + distanceBlock)):
                if xPos in self.blocks and yPos in self.blocks[xPos] and self.blocks[xPos][yPos]:
                    blocks.append(self.blocks[xPos][yPos])
        return blocks

class Block():
    def __init__(self, x, y, BlockType, translucent=False):
        self.color = BlockType
        self.hitbox = pygame.Rect(0, 0, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.hitboxWorldFrame = pygame.Rect(x, y, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.x = x
        self.y = y
        self.highlighted = False
        self.render = False
        self.translucent = translucent

if __name__ == "__main__" :
    World()