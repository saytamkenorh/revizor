import pygame

import data
import scenes
import sprites


class Label(sprites.Widget):
    text: str
    font: pygame.font.Font
    x: float
    y: float

    def __init__(self, x, y, text, font=data.TEXT_FONT):
        super().__init__(x, y, 0, 0)
        self.x = x
        self.y = y
        self.font = font
        self.set_text(text)

    def set_text(self, text: str):
        self.text = text
        w, h = self.font.size(text)
        self.rect.x = self.x - w / 2
        self.rect.y = self.y - h / 2
        self.rect.w = w
        self.rect.h = h

    def update(self, fs: scenes.FrameStatus):
        s = fs.surface
        s.blit(self.font.render(self.text, True, (255, 255, 255)), self.rect)
