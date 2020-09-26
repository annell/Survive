import pygame
import math
from collections import defaultdict
from opensimplex import OpenSimplex
from Common import Physics
from Common import BlockType

class Enviroment():
    def __init__(self, width, height, seed):
        self.blockindex = 0
        self.blocks = defaultdict(lambda : {})
        self.topLayer = defaultdict(lambda : None)
        self.genHills = OpenSimplex(seed)
        self.genCaves = OpenSimplex(seed)
        self.width = width
        self.height = height
        self.GenerateEnviroment()

    def GenerateEnviroment(self):
        for x in range(-self.width, self.width):
            height = -5 * self.Noise(0.01 * x, 0, self.genHills)
            height += -1 * self.Noise(0.06 * x, 0, self.genHills)
            height += -0.5 * self.Noise(0.12 * x, 0, self.genHills)
            height = math.pow(height, 3)
            first = True
            for y in range(int(height), self.height):
                if first:
                    if self.GetBlockType(y) == BlockType.WATER:
                        for yn in range(3, y + 1):
                            self.CreateBlock((x, yn), BlockType.WATER)
                    else:
                        self.CreateBlock((x, y), self.GetBlockType(y))

                    #self.topLayer[x] = (self.blocks[x][y], y)
                    first = False
                else:
                    if self.topLayer[x][0].color == BlockType.GRASS and abs(y - self.topLayer[x][1]) < 3:
                        self.CreateBlock((x, y), BlockType.DIRT)
                    else:
                        self.CreateBlock((x, y), BlockType.STONE)

        #Caves
        for x in range(-self.width, self.width):
            if x in self.topLayer:
                for y in range(self.topLayer[x][1], self.height):
                    cave = 1 * self.Noise(0.02 * x, 0.05 * y, self.genCaves) 
                    if cave < -0.4 and self.blocks[x][y].color != BlockType.WATER:
                        self.blocks[x].pop(y, None)
        
        self.StartSpread()

        #Spread water
    def StartSpread(self):
        visited = defaultdict(lambda : defaultdict(lambda : False))
        for x in range(-self.width, self.width):
            for y in range(self.topLayer[x][1], self.height):
                if y in self.blocks[x]:
                    if self.blocks[x][y].color == BlockType.WATER:
                        try:
                            self.SpreadWater(x + 1, y, visited)
                            self.SpreadWater(x - 1, y, visited)
                            self.SpreadWater(x, y + 1, visited)
                        except RecursionError:
                            print("Max recursion hit around: (", x, ",", y, ")")
    
    def SpreadWater(self, x, y, visited):
        if y in self.blocks[x]:
            return
        if visited[x][y]:
            return
        visited[x][y] = True
        if x > -Physics.MAPWIDTH and x < Physics.MAPWIDTH and y > -Physics.MAPDEPTH and y < Physics.MAPDEPTH:
            self.CreateBlock((x, y), BlockType.WATER)
            self.SpreadWater(x + 1, y, visited)
            self.SpreadWater(x - 1, y, visited)
            self.SpreadWater(x, y + 1, visited)

    def GetBlockType(self, y):
        if y > 2:
            return BlockType.WATER
        if y > 0:
            return BlockType.DIRT
        if y > -20:
            return BlockType.GRASS
        if y > -30:
            return BlockType.STONE
        return BlockType.SNOW
    
    def BlockAt(self, pos):
        x, y = pos
        if x in self.blocks and y in self.blocks[x] and self.blocks[x][y]:
            return self.blocks[x][y]
        return None
    
    def IsAdjecentBlock(self, pos):
        x, y = pos
        if self.BlockAt((x + 1, y)):
            return True
        if self.BlockAt((x - 1, y)):
            return True
        if self.BlockAt((x, y + 1)):
            return True
        if self.BlockAt((x, y - 1)):
            return True
        return False

    def BlocksAt(self, pos, distance=20):
        blocks = []
        x, y = pos
        xBlock = (x) / Physics.BLOCKWIDTH
        yBlock = (y) / Physics.BLOCKHEIGHT
        distanceBlock = distance / Physics.BLOCKWIDTH
        for xPos in range(round(xBlock - distanceBlock), round(xBlock + distanceBlock)):
            for yPos in range(round(yBlock - distanceBlock), round(yBlock + distanceBlock)):
                block = self.BlockAt((xPos, yPos))
                if block:
                    blocks.append(block)
        return blocks
    
    def BlocksInArea(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        xMin = min(x1, x2)
        xMax = max(x1, x2)
        yMin = min(y1, y2)
        yMax = max(y1, y2)
        blocks = []
        for x in range(round(xMin / Physics.BLOCKWIDTH), round(xMax / Physics.BLOCKWIDTH)):
            for y in range(round(yMin / Physics.BLOCKHEIGHT), round(yMax / Physics.BLOCKHEIGHT)):
                block = self.BlockAt((x, y))
                if block:
                    blocks.append(block)
        return blocks
    
    def Noise(self, x, y, gen):
        return gen.noise2d(x, y)

    def GetTopLayerCoordinate(self, x):
        block = self.BlockAt((x, self.topLayer[x][1]))
        if not block:
            for y in range(self.height, -self.height, -1):
                block = self.BlockAt((x, y))
                if block:
                    self.topLayer[x] = (block, y)
        return self.topLayer[x][1]
    
    def CreateBlock(self, pos, blockType):
        x, y = pos
        block = Block(self.blockindex, x*Physics.BLOCKWIDTH, y*Physics.BLOCKHEIGHT, blockType)
        self.blocks[x][y] = block
        self.blockindex += 1
        if x in self.topLayer:
            yTop = self.topLayer[x][1]
            if yTop > y:
                self.topLayer[x] = (block, y)
        else:
            self.topLayer[x] = (block, y)
        return block

    def DeleteBlock(self, block):
        x = (block.hitboxWorldFrame.x) / Physics.BLOCKWIDTH
        y = (block.hitboxWorldFrame.y) / Physics.BLOCKHEIGHT
        self.blocks[x].pop(y, None)

class Block():
    def __init__(self, id, x, y, BlockType, translucent=False):
        self.id = id
        self.color = BlockType
        self.hitbox = pygame.Rect(0, 0, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.hitboxWorldFrame = pygame.Rect(x, y, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.x = x
        self.y = y
        self.highlighted = False
        self.render = False
        self.translucent = translucent
    
    def GetPosition(self):
        return (self.x, self.y)