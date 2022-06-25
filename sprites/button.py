from typing import Callable
import pygame

import sprites
import scenes
import data


class Button(sprites.Widget):
    text: str
    x: float
    y: float
    on_clicked_callback: Callable
    on_clicked_callback_data: list
    active: bool

    def __init__(self, x, y, text):
        super().__init__(x, y, 0, 0)
        self.x = x
        self.y = y
        self.set_text(text)
        self.on_clicked_callback = None
        self.on_clicked_callback_data = []
        self.active = True

    def set_text(self, text: str):
        self.text = text
        f = data.FONT
        w, h = f.size(text)
        self.rect.x = self.x - w / 2
        self.rect.y = self.y - h / 2
        self.rect.w = w
        self.rect.h = h

    def update(self, fs: scenes.FrameStatus):
        s = fs.surface
        f = data.FONT
        bgr = self.rect.inflate(16, 16)

        if self.active:
            color = (230, 220, 0)
            color_border = (255, 100, 0)
        else:
            color = (230, 230, 230)
            color_border = (255, 255, 255)

        pygame.draw.rect(s, color, bgr, border_radius=3)
        pygame.draw.rect(s, color_border, bgr, width=3, border_radius=3)
        s.blit(f.render(self.text, True, (255, 255, 255)), self.rect)

    def on_clicked(self, event):
        if not self.active:
            return
        if callable(self.on_clicked_callback):
            self.on_clicked_callback(*self.on_clicked_callback_data)
