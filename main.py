import math
import random
import time

import pygame
from pygame.locals import *

from Camera import Camera
from Common import Direction, Physics, Screen, BlockType, Item
from Creature import Player
from Engine import Engine 
from Enviroment import Enviroment 



class App:
    def __init__(self):
        self._running = True
        self._close = False
        self.size = self.weight, self.height = Screen.WIDTH, Screen.HEIGHT
        self.fps = Physics.FPS
        self.playtime = 0.0
        self.lastTime = time.time()
        self.currFps = 0
        self.clock = pygame.time.Clock()
        pygame.mixer.init()
        pygame.init()
        pygame.display.set_caption("Survive")
 
    def on_init(self):
        self.camera = Camera(Screen.WIDTH, Screen.HEIGHT, Physics.BLOCKWIDTH, Physics.BLOCKHEIGHT)
        self.enviroment = Enviroment(Physics.MAPWIDTH, Physics.MAPDEPTH, int(random.random() * 100000.0))
        self.world = Engine(pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE), self.camera, self.enviroment)
        self.player = Player(0, -35)
        #self.world.AddLight(self.player)
        self.entities = [self.player]
        self._running = True
        self.visionLines = []
        self.font = pygame.font.SysFont('mono', 16)
        self.n = 0
        self.camera.SetFocusPos(self.entities[self.n])
 
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
            elif event.key == pygame.K_n:
                self.n += 1
                if self.n >= len(self.entities):
                    self.n = 0
                self.camera.SetFocusPos(self.entities[self.n])
            elif event.key == pygame.K_1:
                self.player.currentItem = Item.PICKAXE
            elif event.key == pygame.K_2:
                self.player.currentItem = BlockType.STONE
            elif event.key == pygame.K_3:
                self.player.currentItem = BlockType.GRASS
            elif event.key == pygame.K_4:
                self.player.currentItem = BlockType.DIRT
            elif event.key == pygame.K_5:
                self.player.currentItem = BlockType.BEACH
            elif event.key == pygame.K_6:
                self.player.currentItem = BlockType.LIGHT
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                self.player.Move(Direction.RIGHT, False)
            elif event.key == pygame.K_a:
                self.player.Move(Direction.LEFT, False)
            elif event.key == pygame.K_s:
                self.player.Move(Direction.DOWN, False)
            elif event.key == pygame.K_SPACE:
                self.player.Move(Direction.UP, False)
         
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.player.Action(self.world, self.camera.CameraToWorld(pygame.mouse.get_pos()))

    def on_loop(self):
        self.world.SpawnCreatures(self.player, self.entities)
        for entity in self.entities:
            entity.Step()
        self.world.CollisionCheck(self.entities)
        self.camera.PlaceInScene(self.entities)
        self.player.SelectBlock(self.camera.CameraToWorld(pygame.mouse.get_pos()), self.world)

        self.world.renderedBlocks.clear()
        for block in self.enviroment.BlocksAt(self.player.GetPosition(), 500):
            self.world.renderedBlocks[block.id] = block
        self.world.LightSource(self.player.GetPosition())

        
    def on_render(self):
        self.draw_background()
        self.world.RenderBlocks()
        self.draw_hud()
        self.draw_entities()
        pygame.display.update()
    
    def draw_background(self):
        self.world._display_surf.fill((10, 160, 250))
    
    def draw_entities(self):
        for entity in self.entities:
            pygame.draw.rect(self.world._display_surf, entity.color, entity.hitbox)
    
    def draw_hud(self):
        self.draw_playerInteraction()

        self.draw_text("({}, {}) @ World: {} | {}".format(*self.player.GetPosition(), self.enviroment.seed, self.player.onGround), (0,0))
        self.draw_text("FPS: {}".format(self.currFps), (0, 10))
        self.draw_text("Press R to restart", (0, 20))
        self.draw_text("Press ESC to exit", (0, 30))
        self.draw_text("Press p to pause", (0, 40))
        self.draw_text("({}, {})".format(*self.camera.CameraToBlockgrid(pygame.mouse.get_pos())), (0, 70))
        block = self.world.BlockAt(self.camera.CameraToBlockgrid(pygame.mouse.get_pos()))
        if block:
            self.draw_text("({}, {}) Color: {}".format(*self.camera.CameraToBlockgrid((block.hitboxWorldFrame.x, block.hitboxWorldFrame.y)), block.color), (0, 80))
    
    def draw_playerInteraction(self):
        center = self.camera.WorlToCamera(self.player.GetPositionCentered())
        mouse = self.camera.CameraToWorld(pygame.mouse.get_pos())
        player = self.player.GetPositionCentered() 
        distPos = self.world.GetPointAlongLineAtDistance((player, mouse), self.player.reach)
        pygame.draw.line(self.world._display_surf, self.player.currentItem, center, (center[0] + distPos[0], center[1] + distPos[1]), 5)
    
    def draw_text(self, text, position):
        surface = self.font.render(text, True, (255, 255, 255))
        self.world._display_surf.blit(surface, position)

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( not self._close ):
            currTime = time.time()
            self.currFps = int(1 /(currTime - self.lastTime))
            self.lastTime = currTime
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
