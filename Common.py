from enum import Enum

class Direction(Enum):
    UP = "UP"
    DOWN  = "DOWN"
    RIGHT = "RIGHT"
    LEFT = "LEFT"

class Biome():
    WATER = (0, 0, 255, 128)
    STONE = (100, 100, 100)
    DIRT = (128, 64, 0)
    GRASS = (0, 255, 0)
    SNOW = (255, 255, 255)
    BEACH = (203, 201, 105)

class Physics():
    FPS = 120
    BLOCKWIDTH = 20
    BLOCKHEIGHT = 20
    GRAVITY = 9.81
    MAXVSPEED = 5
    MAXHSPEED = 2
    MAPWIDTH = 500
    MAPDEPTH = 100
    JUMPHEIGHT = -2.5
    SPAWNDISTANCE = 10000
    NRCREATURES = 15

class Screen():
    WIDTH = 1000
    HEIGHT = 400
    RENDERDISTANCE = 500
    RAYDISTANCE = 300