import pygame
from Common import Screen
import math

class Camera():
    def __init__(self): 
        self.cameraFrame = pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT)
    
    def PlaceInScene(self, pos, blocks):
        x, y = self.CenterOfFrame(pos)
        self.cameraFrame.x = x
        self.cameraFrame.y = y
        for block in blocks:
            block.hitbox.x = block.x - x
            block.hitbox.y = block.y - y

    def CenterOfFrame(self, pos):
        x, y = pos
        return (x - Screen.WIDTH/2, y - Screen.HEIGHT/2)
    
    def CameraToWorld(self, pos):
        x, y = pos
        return x + self.cameraFrame.x, y + self.cameraFrame.y

    def GetCenterScreen(self):
        x = self.cameraFrame.x + Screen.WIDTH/2
        y = self.cameraFrame.y + Screen.HEIGHT/2
        return (x, y)
