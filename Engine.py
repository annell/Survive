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
        self.renderedBlocks = {}
    
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
    
    def GetNormalizedVector(self, ray):
        dx0 = ray[0][0] - ray[1][0]
        dy0 = ray[0][1] - ray[1][1]
        x0 = ray[0][0]
        y0 = ray[0][1]
        dx = dx0/(abs(dx0) + abs(dy0))
        dy = dy0/(abs(dx0) + abs(dy0))
        return (dx, dy)
    
    def GetPointAlongLineAtDistance(self, ray, distance):
        dx = ray[0][0] - ray[1][0]
        dy = ray[0][1] - ray[1][1]
        t = math.atan2(dy, dx)
        x = math.cos(t) * distance * -1
        y = math.sin(t) * distance * -1
        return x, y
    
    def ClosestIntersectingBlock2(self, ray, ignoreBlock):
        closestBlock = None
        closestDist = 10000000
        n = 0
        for block in self.enviroment.BlocksInArea(*ray):
            if block == ignoreBlock:
                pass
            line = (ray[0], block.GetPosition())
            distance = self.GetDistance(*line)
            if distance < closestDist:
                if self.LineBlockCollision(line, block):
                    n +=1
                    closestBlock = block
                    closestDist = distance
        return closestBlock
    
    def ClosestIntersectingBlock(self, ray, distance, ignoreBlock=None):
        dx, dy = self.GetNormalizedVector(ray)
        x = x0 = ray[0][0]
        y = y0 = ray[0][1]
        stepsize = 20
        for _ in range(0, distance):
            x -= dx * stepsize
            y -= dy * stepsize
            if self.GetDistance((x0, y0), (x, y)) >= distance:
                return None
            block = self.BlockAt(self.camera.WorldToBlockgrid((x, y)))
            if block:
                if ignoreBlock == block:
                    return None
                return block

    def RenderBlocks(self):
        self.camera.PlaceInScene(self.renderedBlocks.values())
        for block in self.renderedBlocks.copy().values():
            if block.highlighted:
                self.RenderHighlight(block)
            else:
                self.RenderBlock(block)
            block.render = 0

    def RenderBlock(self, block):
        illumination = block.render / 100
        if illumination > 1:
            illumination = 1
        if illumination < 0:
            illumination = 0
        r, g, b = block.color
        pygame.draw.rect(self._display_surf, (r*illumination, g*illumination, b*illumination), block.hitbox)

    def RenderHighlight(self, block):
        r, g, b = block.color
        r *= 1.5
        g *= 0.5
        b *= 0.5
        if r > 255:
            r = 255
        if r < 100:
            r = 100
        if g < 0:
            g = 0
        if b < 0:
            b = 0
        pygame.draw.rect(self._display_surf, (r, g, b), block.hitbox)
        block.highlighted = False
    
    def SpawnCreatures(self, player, creatures):
        for creature in creatures:
            if self.GetDistance(player.GetPosition(), creature.GetPosition()) > Physics.SPAWNDISTANCE:
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

    def LightSource(self, pos):
        camX, camY = self.camera.CameraTopLeftCornerWorldFrame(pos)
        cam2X, cam2Y = self.camera.CameraBottomRightCornerWorldFrame(pos)
        blockPos = self.camera.WorldToBlockgrid((camX, camY))
        blockPos2 = self.camera.WorldToBlockgrid((cam2X, cam2Y))
        b1X, _ = blockPos
        b2X, _ = blockPos2
        for x in range(b1X, b2X):
            y = self.enviroment.GetTopLayerCoordinate(x)
            block = self.enviroment.BlockAt((x, y))
            if block:
                if block.color == BlockType.WATER:
                    yTemp = y
                    blocks = []
                    while block:
                        blocks.append(block)
                        yTemp -= 1
                        block = self.enviroment.BlockAt((x, yTemp))
                    render = 100
                    for b in reversed(blocks):
                        b.render = render
                        render -= 7
                        self.renderedBlocks[b.id] = b
                        if render <= 0:
                            break
                    if render > 0:
                        block = self.enviroment.BlockAt((x, y + 1))
                        if block:
                            block.render = render - 7
                            self.renderedBlocks[block.id] = block
                else:
                    block.render = 100
                    self.renderedBlocks[block.id] = block
        self.RaytraceRandom(pos)
        #self.RaytraceEachBlock(pos)

    def RaytraceEachBlock(self, pos):
        for light in self.lightSources:
            if self.GetDistance(light.GetPosition(), pos) < Screen.RENDERDISTANCE:
                light.render = 100
                x, y = light.x, light.y 
                x += Physics.BLOCKWIDTH/2
                y += Physics.BLOCKHEIGHT/2
                for targetBlock in self.enviroment.BlocksAt(light.GetPosition(), Screen.RAYDISTANCE):
                    if targetBlock != light:
                        closestBlock = None
                        closestDist = 10000000
                        n = 0
                        for block in self.enviroment.BlocksInArea(light.GetPosition(), targetBlock.GetPosition()):
                            line = (light.GetPosition(), block.GetPosition())
                            distance = self.GetDistance(*line)
                            if distance < closestDist:
                                if self.LineBlockCollision(line, block):
                                    n +=1
                                    closestBlock = block
                                    closestDist = distance
                        block = closestBlock
                        if block:
                            distance = self.GetDistance(light.GetPosition(), block.GetPosition())
                            block.render += 100*(Screen.RAYDISTANCE - distance)/Screen.RAYDISTANCE
                            self.renderedBlocks[block.id] = block
    
    def RaytraceRandom(self, pos):
        maxRays = 50
        for light in self.lightSources:
            if self.GetDistance(light.GetPosition(), pos) < Screen.RENDERDISTANCE:
                light.render = 100
                nrRays = 100
                x, y = light.x, light.y 
                x += Physics.BLOCKWIDTH/2
                y += Physics.BLOCKHEIGHT/2
                for n in range(nrRays):
                    angle = (n/nrRays)*2*math.pi
                    dx = math.cos(angle)
                    dy = math.sin(angle)
                    rx = x + dx
                    ry = y + dy
                    #block = self.ClosestIntersectingBlock2(((x, y), (rx, ry)), ignoreBlock=light)
                    block = self.ClosestIntersectingBlock(((x, y), (rx, ry)), Screen.RAYDISTANCE, ignoreBlock=light)
                    if block:
                        distance = self.GetDistance(light.GetPosition(), block.GetPosition())
                        block.render += 100*(Screen.RAYDISTANCE - distance)/Screen.RAYDISTANCE
                        self.renderedBlocks[block.id] = block

    def LineBlockCollision(self, line, block):
        if self.LinesIntersects(line, (block.hitboxWorldFrame.topleft, block.hitboxWorldFrame.topright)):
            return True
        if self.LinesIntersects(line, (block.hitboxWorldFrame.bottomleft, block.hitboxWorldFrame.bottomright)):
            return True
        if self.LinesIntersects(line, (block.hitboxWorldFrame.topleft, block.hitboxWorldFrame.bottomleft)):
            return True
        if self.LinesIntersects(line, (block.hitboxWorldFrame.bottomright, block.hitboxWorldFrame.topright)):
            return True
        return False

    def LinesIntersects(self, s0, s1):
        dx0 = s0[1][0] - s0[0][0]
        dx1 = s1[1][0] - s1[0][0]
        dy0 = s0[1][1] - s0[0][1]
        dy1 = s1[1][1] - s1[0][1]
        p0 = dy1*(s1[1][0]-s0[0][0]) - dx1*(s1[1][1]-s0[0][1])
        p1 = dy1*(s1[1][0]-s0[1][0]) - dx1*(s1[1][1]-s0[1][1])
        p2 = dy0*(s0[1][0]-s1[0][0]) - dx0*(s0[1][1]-s1[0][1])
        p3 = dy0*(s0[1][0]-s1[1][0]) - dx0*(s0[1][1]-s1[1][1])
        return (p0*p1<=0) & (p2*p3<=0)

    def GetDistance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def CreateBlock(self, pos, blockType):
        x, y = self.camera.WorldToBlockgrid(pos)
        if self.BlockAt((x, y)):
            return False
        block = self.enviroment.CreateBlock((x, y), blockType)
        if block.color == BlockType.LIGHT:
            self.AddLight(block)
        else:
            yTop = self.enviroment.GetTopLayerCoordinate(x)
            if yTop > y:
                self.enviroment.topLayer[x] = (block, y)
        return block
    
    def DeleteBlock(self, block):
        if block.id in self.renderedBlocks:
            self.renderedBlocks.pop(block.id)
        if block.color == BlockType.LIGHT:
            self.lightSources.remove(block)
        self.enviroment.DeleteBlock(block)
    
    def BlockAt(self, pos):
        return self.enviroment.BlockAt(pos)
