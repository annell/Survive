import unittest
from Camera import Camera

class TestCamera(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(100, 100, 20, 20)
    
    def test_Focus(self):
        self.assertEqual(self.camera.GetFocusPos(), None)       
        focus = focusMock()
        self.camera.SetFocusPos(focus)
        self.assertEqual(self.camera.GetFocusPos(), (12, 34))
    
    def test_CenterScreenAtFocus(self):
        focus = focusMock()
        self.assertEqual(self.camera.cameraFrame.x, 0)
        self.assertEqual(self.camera.cameraFrame.y, 0)
        self.camera.CenterScreenAtFocus()
        self.assertEqual(self.camera.cameraFrame.x, 0)
        self.assertEqual(self.camera.cameraFrame.y, 0)
        self.camera.SetFocusPos(focus)
        self.assertEqual(self.camera.cameraFrame.x, 0)
        self.assertEqual(self.camera.cameraFrame.y, 0)
        self.camera.CenterScreenAtFocus()
        self.assertEqual(self.camera.cameraFrame.x, -38)
        self.assertEqual(self.camera.cameraFrame.y, -16)
    
    def test_CameraCornerWorldFrame(self):
        x, y = self.camera.CameraCornerWorldFrame((100, 100))
        self.assertEqual(x, 50)
        self.assertEqual(y, 50)

    def test_CameraToWorld(self):
        x, y = self.camera.CameraToWorld((100, 100))
        self.assertEqual(x, 100)
        self.assertEqual(y, 100)
        focus = focusMock()
        self.camera.SetFocusPos(focus)
        self.camera.CenterScreenAtFocus()
        x, y = self.camera.CameraToWorld((100, 100))
        self.assertEqual(x, 62)
        self.assertEqual(y, 84)

    def test_CameraToBlockgrid(self):
        pos = (27.1, 200.7)
        self.assertEqual(self.camera.CameraToBlockgrid(pos), (1, 10))
        focus = focusMock()
        self.camera.SetFocusPos(focus)
        self.camera.CenterScreenAtFocus()
        self.assertEqual(self.camera.CameraToBlockgrid(pos), (-1, 9))

    def test_WorldToBlockgrid(self):
        pos = (27.1, 200.7)
        self.assertEqual(self.camera.WorldToBlockgrid(pos), (1, 10))


class focusMock():
    def GetPosition(self):
        return (12, 34)

if __name__ == '__main__':
    unittest.main()