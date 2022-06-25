#!/usr/bin/python3
import sys

import pygame
import pygame.locals as pygl

import scenes
import data

pygame.init()

fps = 30
fpsClock = pygame.time.Clock()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Revizor")

scenestatus = scenes.SceneStatus()
scenestatus.add_scene("menu", scenes.MenuScene)
scenestatus.add_scene("tutorial", scenes.TutorialScene)
scenestatus.add_scene("setup", scenes.SetupScene)
scenestatus.add_scene("game", scenes.GameScene)
scenestatus.set_scene("menu")

try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

pygame.display.set_icon(data.get_img("icon.png", 1))

# Game loop
while True:
    screen.fill((0, 0, 0))

    events = pygame.event.get()
    for event in events:
        if event.type == pygl.QUIT:
            pygame.quit()
            sys.exit()

    fs = scenes.FrameStatus(fpsClock, screen, events)
    scenestatus.render_current(fs)

    pygame.display.flip()
    fpsClock.tick(fps)
