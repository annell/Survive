import pygame

class Camera():
    def __init__(self, width, height, blockWidth, blockHeight): 
        self.width = width
        self.height = height
        self.blockWidth = blockWidth
        self.blockHeight = blockHeight
        self.cameraFrame = pygame.Rect(0, 0, self.width, self.height)
        self.focus = None
    
    def SetFocusPos(self, focus):
        self.focus = focus
    
    def GetFocusPos(self):
        if not self.focus:
            return None
        return self.focus.GetPosition()
    
    def CenterScreenAtFocus(self):
        pos = self.GetFocusPos()
        if not pos:
            return
        self.cameraFrame.x, self.cameraFrame.y = self.CameraCornerWorldFrame(pos)
    
    def PlaceInScene(self, objects):
        self.CenterScreenAtFocus()
        for obj in objects:
            obj.hitbox.x = obj.x - self.cameraFrame.x
            obj.hitbox.y = obj.y - self.cameraFrame.y

    def CameraCornerWorldFrame(self, pos):
        x, y = pos
        return (x - self.width/2, y - self.height/2)
    
    def CameraToWorld(self, pos):
        x, y = pos
        return x + self.cameraFrame.x, y + self.cameraFrame.y

    def CameraToBlockgrid(self, pos):
        return self.WorldToBlockgrid(self.CameraToWorld(pos))
    
    def WorldToBlockgrid(self, pos):
        x, y = pos
        return (round(x/self.blockWidth - 0.5), round(y/self.blockHeight - 0.5))
