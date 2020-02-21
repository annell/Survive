import pygame
from Common import Screen, Physics
import math

class Camera():
    def __init__(self): 
        self.cameraFrame = pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT)
    
    def CenterScreenAt(self, pos):
        x, y = self.WorldToCamera(pos)
        self.cameraFrame.x = x
        self.cameraFrame.y = y
    
    def PlaceInScene(self, pos, objects):
        x, y = self.WorldToCamera(pos)
        for obj in objects:
            obj.hitbox.x = obj.x - x
            obj.hitbox.y = obj.y - y

    def WorldToCamera(self, pos):
        x, y = pos
        return (x - Screen.WIDTH/2, y - Screen.HEIGHT/2)
    
    def CameraToWorld(self, pos):
        x, y = pos
        return x + self.cameraFrame.x, y + self.cameraFrame.y

    def GetCenterScreenWorldFrame(self):
        x = (self.cameraFrame.x + Screen.WIDTH/2)/Physics.BLOCKWIDTH
        y = (self.cameraFrame.y + Screen.HEIGHT/2)/Physics.BLOCKHEIGHT
        return (x, y)

    def GetCenterScreenCameraFrame(self):
        x = Screen.WIDTH/2
        y = Screen.HEIGHT/2
        return (x, y)
