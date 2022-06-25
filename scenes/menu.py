import pygame
import pygame.locals as pygl

import scenes
import sprites
import data


class MenuScene(scenes.Scene):
    widgets: sprites.WidgetGroup

    def __init__(self, scene_status: scenes.SceneStatus):
        super().__init__(scene_status)
        w, h = scene_status.get_screen_size()
        self.widgets = sprites.WidgetGroup()

        lbl = sprites.Label(w / 2, h / 2 - 200, "Revizor", data.TITLE_FONT)
        self.widgets.add(lbl)

        lbl_author = sprites.Label(
            w / 2, h / 2 + 250,
            "© Matyáš Hronek 2022", data.TEXT_FONT)
        self.widgets.add(lbl_author)

        btn_play = sprites.Button(w / 2, h / 2 - 100, "Hrát")
        btn_play.on_clicked_callback = self.on_play
        self.widgets.add(btn_play)

        btn_tutorial = sprites.Button(w / 2, h / 2 - 50, "Návod")
        btn_tutorial.on_clicked_callback = self.on_tutorial
        self.widgets.add(btn_tutorial)

        btn_exit = sprites.Button(w / 2, h / 2 - 0, "Konec")
        btn_exit.on_clicked_callback = self.on_exit
        self.widgets.add(btn_exit)

    def on_play(self):
        self.scene_status.set_scene("setup")

    def on_tutorial(self):
        self.scene_status.set_scene("tutorial")

    def on_exit(self):
        pygame.event.post(pygame.event.Event(pygl.QUIT))

    def render(self, fs: scenes.FrameStatus):
        self.widgets.update(fs)
