import typing
import pygame
import pygame.locals as pygl
import scenes


class OnClickedEvent(typing.NamedTuple):
    x: int
    y: int


class WidgetGroup(pygame.sprite.Group):

    def __init__(self) -> None:
        super().__init__([])

    def update(self, fs: scenes.FrameStatus):
        for event in fs.events:
            if event.type == pygl.MOUSEBUTTONDOWN:
                x, y = event.pos
                for widget in reversed(self.sprites()):
                    if widget.rect.collidepoint(x, y) and widget.visible:
                        widget.on_clicked(OnClickedEvent(
                            x - widget.rect.x,
                            y - widget.rect.y))
                        break
        for widget in self:
            widget.update_always(fs)
            if widget.visible:
                widget.update(fs)


class Widget(pygame.sprite.Sprite):
    rect: pygame.Rect
    visible: bool

    def __init__(self, x, y, w, h):
        super().__init__([])
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True

    def update(self, fs: scenes.FrameStatus):
        pass

    def update_always(self, fs: scenes.FrameStatus):
        pass

    def on_clicked(self, event):
        pass
