import pygame
import random
import math
from collections import defaultdict

from Common import Physics
from Common import Biome
from Common import Screen 

from Creature import Pigg
from Creature import Zombie
from Creature import Sheep

from opensimplex import OpenSimplex
import math

class World():
    def __init__(self):
        self.seed = int(random.random() * 100000.0)
        genHills = OpenSimplex(self.seed)
        genCaves = OpenSimplex(self.seed)
        self.blocks = defaultdict(lambda : {})
        self.renderedBlocks = []
        self.topLayer = defaultdict(lambda : None)
        for x in range(-Physics.MAPWIDTH, Physics.MAPWIDTH):
            height = -5 * self.noise(0.01 * x, 0, genHills)
            height += -1 * self.noise(0.06 * x, 0, genHills)
            height += -0.5 * self.noise(0.12 * x, 0, genHills)
            height = math.pow(height, 3)
            first = True
            for y in range(int(height), Physics.MAPDEPTH):
                if first:
                    if self.GetBiome(y) == Biome.WATER:
                        for yn in range(3, y + 1):
                            self.blocks[x][yn] = Block(x*Physics.BLOCKWIDTH, yn*Physics.BLOCKHEIGHT, Biome.WATER)
                    else:
                        self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, self.GetBiome(y))

                    self.topLayer[x] = (self.blocks[x][y], y)
                    first = False
                else:
                    if self.topLayer[x][0].color == Biome.GRASS and abs(y - self.topLayer[x][1]) < 3:
                        self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, Biome.DIRT)
                    else:
                        self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, Biome.STONE)

        #Caves
        for x in range(-Physics.MAPWIDTH, Physics.MAPWIDTH):
            if x in self.topLayer:
                for y in range(self.topLayer[x][1], Physics.MAPDEPTH):
                    cave = 1 * self.noise(0.02 * x, 0.05 * y, genCaves) 
                    if cave < -0.4 and self.blocks[x][y].color != Biome.WATER:
                        self.blocks[x].pop(y, None)

        #Spread water
        #visited = defaultdict(lambda : defaultdict(lambda : False))
        #for x in range(-Physics.MAPWIDTH, Physics.MAPWIDTH):
        #    for y in range(self.topLayer[x][1], Physics.MAPDEPTH):
        #        if y in self.blocks[x]:
        #            if self.blocks[x][y].color == Biome.WATER:
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
                self.blocks[x][y] = Block(x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, Biome.WATER)
                self.SpreadWater(x + 1, y, visited)
                self.SpreadWater(x - 1, y, visited)
                self.SpreadWater(x, y + 1, visited)
        
    def GetBiome(self, y):
        #if y > 2:
        #    return Biome.WATER
        if y > 0:
            return Biome.DIRT
        if y > -20:
            return Biome.GRASS
        if y > -30:
            return Biome.STONE
        return Biome.SNOW
    
    def noise(self, x, y, gen):
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
                if block.color == Biome.WATER:
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
    
    def closestIntersectingBlock(self, ray, distance):
        dx0 = ray[0][0] - ray[1][0]
        dy0 = ray[0][1] - ray[1][1]
        x0 = ray[0][0]
        y0 = ray[0][1]
        stepsize = 1
        dx = dx0/(abs(dx0) + abs(dy0))
        dy = dy0/(abs(dx0) + abs(dy0))
        x = x0
        y = y0
        for n in range(0, distance):
            x -= dx * 10
            y -= dy * 10
            if math.hypot(x - x0, y - y0) > distance:
                return None
            blocks = self.BlocksAt((x, y), 10)
            if blocks:
                for block in blocks:
                    return block
    
    def SpawnCreatures(self, player, creatures):
        for creature in creatures:
            if abs(player.x - creature.x) > Physics.SPAWNDISTANCE:
                creatures.remove(creature)
        for n in range(Physics.NRCREATURES - len(creatures)):
            r = random.random()
            x = random.randrange(-Physics.SPAWNDISTANCE, Physics.SPAWNDISTANCE)
            y = self.GetTopLayerCoordinate(int(x/Physics.BLOCKWIDTH)) - 1
            y *= Physics.BLOCKHEIGHT
            if r < 0.05:
                creatures.append(Zombie(x, y))
            elif r < 0.4:
                creatures.append(Sheep(x, y))
            else:
                creatures.append(Pigg(x, y))


    def Blocks(self):
        return self.blocks
    
    def GetTopLayerCoordinate(self, x):
        return self.topLayer[x][1]
    
    def BlocksAt(self, pos, distance):
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
    
    def DeleteBlock(self, block):
        x = (block.hitboxWorldFrame.x) / Physics.BLOCKWIDTH
        y = (block.hitboxWorldFrame.y) / Physics.BLOCKHEIGHT
        self.blocks[x].pop(y, None)

class Block():
    def __init__(self, x, y, biome):
        self.color = biome
        self.hitbox = pygame.Rect(0, 0, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.hitboxWorldFrame = pygame.Rect(x, y, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.x = x
        self.y = y
        self.highlighted = False
        self.render = False

if __name__ == "__main__" :
    World()