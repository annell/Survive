import math
import random

import pygame
from pygame.locals import *

from Camera import Camera
from Common import Direction, Physics, Screen
from Creature import *
from World import World


class App:
    def __init__(self):
        self._running = True
        self._close = False
        self._display_surf = None
        self.size = self.weight, self.height = Screen.WIDTH, Screen.HEIGHT
        self.fps = Physics.FPS
        self.playtime = 0.0
        self.clock = pygame.time.Clock()
        pygame.mixer.init()
        pygame.init()
        pygame.display.set_caption("Survive")
        self.visibilityLimited = True
        self.visionLines = []
 
    def on_init(self):
        self.camera = Camera()
        self.world = World()
        self.player = Player(0, -35)
        self.entities = [self.player]
        self._display_surf = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE)
        self._running = True

        self.font = pygame.font.SysFont('mono', 14, bold=True)
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._close = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.player.Move(Direction.RIGHT, True)
            elif event.key == pygame.K_a:
                self.player.Move(Direction.LEFT, True)
            elif event.key == pygame.K_s:
                self.player.Move(Direction.DOWN, True)
            elif event.key == pygame.K_SPACE:
                self.player.Move(Direction.UP, True)
            elif event.key == pygame.K_ESCAPE:
                self._close = True
            elif event.key == pygame.K_r:
                self.on_init()
            elif event.key == pygame.K_p:
                self._running = not self._running
            elif event.key == pygame.K_v:
               self.visibilityLimited = not self.visibilityLimited 
                
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                self.player.Move(Direction.RIGHT, False)
            elif event.key == pygame.K_a:
                self.player.Move(Direction.LEFT, False)
            elif event.key == pygame.K_s:
                self.player.Move(Direction.DOWN, False)
            elif event.key == pygame.K_SPACE:
                self.player.Move(Direction.UP, False)
         
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.player.Action(self.world)

    def on_loop(self):
        self.world.SpawnCreatures(self.player, self.entities)
        for entity in self.entities:
            entity.Step()
        self.world.CollisionCheck(self.entities)
        x, y = self.camera.CameraToWorld(pygame.mouse.get_pos())
        block = self.world.closestIntersectingBlock(((self.player.x + self.player.width/2, self.player.y + self.player.height/2), (x, y)), 30)
        self.player.SelectBlock(block, (x, y))
        if self.visibilityLimited:
            self.render360()

    def render360(self):
        nrRays = 50
        self.visionLines = []
        for _ in range(nrRays):
            angle = random.random()*2*math.pi
            dx = math.cos(angle)
            dy = math.sin(angle)
            x = self.player.x + self.player.width/2
            y = self.player.y
            rx = x + dx
            ry = y + dy
            block = self.world.closestIntersectingBlock(((x, y), (rx, ry)), Screen.RAYDISTANCE)
            if block:
                self.visionLines.append((x, y, block))
                block.render = 2000
        
        
    def on_render(self):
        self._display_surf.fill((20, 20, 20))

        x, y = self.camera.CameraToWorld(pygame.mouse.get_pos())
        #world
        blocks = self.world.BlocksAt(self.player.GetPosition(), Screen.RENDERDISTANCE)
        self.camera.PlaceInScene(self.player.GetPosition(), blocks)
        for block in blocks:
            if block.render or not self.visibilityLimited:
                if block.highlighted:
                    pygame.draw.rect(self._display_surf, (255, 0, 0), block.hitbox)
                    block.highlighted = False
                else:
                    pygame.draw.rect(self._display_surf, block.color, block.hitbox)
                if self.visibilityLimited:
                    block.render -= 10

        self.camera.PlaceInScene(self.player.GetPosition(), self.entities)
        self.camera.CenterScreenAt(self.player.GetPosition())
        for entity in self.entities:
            pygame.draw.rect(self._display_surf, entity.color, entity.hitbox)

        for line in self.visionLines:
            _, _, block = line
            pygame.draw.line(self._display_surf, (255, 255, 255), self.camera.GetCenterScreenCameraFrame(), (block.hitbox.x, block.hitbox.y))
        
        #Scoreboard
        self.draw_text("({}, {}) @ World: {} | {}".format(*self.camera.GetCenterScreenWorldFrame(), self.world.seed, self.player.onGround), (0,0))
        self.draw_text("Press R to restart", (0, 20))
        self.draw_text("Press ESC to exit", (0, 30))
        self.draw_text("Press p to pause", (0, 40))
        self.draw_text("Press v to toggle visibilty mode", (0, 50))
        self.draw_text("({}, {})".format(x, y), (0, 70))
        startY = 80
        blocksAtMouse = self.world.BlocksAt((x, y), 50)
        #for block in blocksAtMouse:
        #    self.draw_text("({}, {}) Color: {}".format(block.hitboxWorldFrame.x/Physics.BLOCKWIDTH, block.hitboxWorldFrame.y/Physics.BLOCKHEIGHT, block.color), (0, startY))
        #    startY += 10

        pygame.display.update()
    
    def draw_text(self, text, position):
        surface = self.font.render(text, True, (255, 255, 255))
        self._display_surf.blit(surface, position)

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( not self._close ):
            for event in pygame.event.get():
                self.on_event(event)
            if self._running:
                self.on_loop()
                self.on_render()
            else:
                pass
            self.playtime += self.clock.tick(self.fps) / 1000.0
            pygame.display.flip()

        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
