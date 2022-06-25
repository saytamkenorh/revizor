import pygame
import math
import sprites
import gamestate
import scenes
import data

from gamestate import MoveState


class PlayerWidget(sprites.Widget):
    player: gamestate.Player
    state: gamestate.GameState

    def __init__(self, x, y,
                 player: gamestate.Player,
                 state: gamestate.GameState):
        super().__init__(x, y, 100, 140)
        self.player = player
        self.state = state

    def update(self, fs: scenes.FrameStatus):
        s = fs.surface
        f = data.TEXT_FONT

        if self.player.loss_order != 0:
            color = (255, 0, 0)
        elif self.player.win_order != 0:
            color = (0, 255, 0)
        elif self.state.current_player == self.player:
            color = (0, 0, 255)
        else:
            color = (255, 255, 255)

        pygame.draw.rect(
            s, color, self.rect, width=3, border_radius=3)

        s.blit(
            f.render(self.player.name, True, color),
            (self.rect.x + 10, self.rect.y + 10))

        # Money
        s.blit(data.get_img("coin.png", 2),
               (self.rect.x + 10, self.rect.y + 25))
        s.blit(
            f.render(str(int(self.player.money)), True, (255, 255, 255)),
            (self.rect.x + 30, self.rect.y + 25 + 8 - f.get_linesize() / 2))

        # Inventory
        item_size = 32
        for i, item in enumerate(
                sorted(self.player.inventory,
                       key=lambda i: gamestate.CELL_NAMES[i])):
            img = pygame.transform.scale(
                gamestate.get_type_image(item), (item_size, item_size))
            s.blit(
                img,
                (self.rect.x + 4 + item_size * math.floor(i % 3),
                 self.rect.y + 45 + item_size * math.floor(i / 3)))

        # Effects
        x = self.rect.x + 8
        for i in range(self.player.blocked_moves):
            s.blit(data.get_img("stop.png", 2),
                   (x, self.rect.y + 115))
            x += 20
        if self.player.wife_effect:
            s.blit(data.get_img("wife.png", 0.5),
                   (x, self.rect.y + 115))
            x += 20

    def on_clicked(self, event):
        if self.state.move_state == MoveState.YOEMEN_EFFECT:
            if self.player != self.state.current_player:
                self.player.blocked_moves += 1
                self.state.next_player()
