import pygame
import os

pygame.font.init()

IMAGES = {}


def get_img(name: str, scale: float) -> pygame.Surface:
    i = IMAGES.get((name, scale), None)
    if i is not None:
        return i
    p = get_path("textures", name)
    i = pygame.image.load(p)
    if scale != 1.0:
        w = round(i.get_width() * scale)
        h = round(i.get_height() * scale)
        i = pygame.transform.scale(i, (w, h))
    IMAGES[(name, scale)] = i
    return i


def get_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_path(*path: str) -> str:
    return os.path.join(get_dir(), "data", *path)


resource_dir = get_path("")
print(f"Resource dir: {resource_dir}")
TEXT_FONT = pygame.font.Font(
    get_path("fonts", "PressStart2P-Regular.ttf"), 12)
FONT = pygame.font.Font(
    get_path("fonts", "PressStart2P-Regular.ttf"), 20)
TITLE_FONT = pygame.font.Font(
    get_path("fonts", "PressStart2P-Regular.ttf"), 48)
