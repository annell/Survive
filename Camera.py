import pygame
from Common import Screen, Physics
import math

class Camera():
    def __init__(self): 
        self.cameraFrame = pygame.Rect(0, 0, Screen.WIDTH, Screen.HEIGHT)
        self.focus = None
    
    def SetFocusPos(self, focus):
        self.focus = focus
    
    def GetFocusPos(self):
        return self.focus.GetPosition()
    
    def CenterScreenAt(self):
        self.cameraFrame.x, self.cameraFrame.y = self.CameraCornerWorldFrame(self.GetFocusPos())
    
    def PlaceInScene(self, objects):
        self.CenterScreenAt()
        for obj in objects:
            obj.hitbox.x = obj.x - self.cameraFrame.x
            obj.hitbox.y = obj.y - self.cameraFrame.y

    def CameraCornerWorldFrame(self, pos):
        x, y = pos
        return (x - Screen.WIDTH/2, y - Screen.HEIGHT/2)

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
