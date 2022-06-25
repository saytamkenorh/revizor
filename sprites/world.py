import pygame
import math

import sprites
import gamestate
from gamestate import MoveState
import scenes


class WorldWidget(sprites.Widget):
    state: gamestate.GameState
    see_all: bool

    def __init__(self, x, y, w, h, state: gamestate.GameState):
        super().__init__(x, y, w, h)
        self.state = state
        self.see_all = False

    def calc_sizes(self) -> tuple[int, int, int, int]:
        worldsize = len(self.state.world)
        cellsize = min(self.rect.w / worldsize, self.rect.h / worldsize)
        mx = self.rect.x + self.rect.w / 2 - cellsize * worldsize / 2
        my = self.rect.y + self.rect.h / 2 - cellsize * worldsize / 2
        return (worldsize, cellsize, mx, my)

    def update(self, fs: scenes.FrameStatus):
        s = fs.surface
        pygame.draw.rect(
            s, (255, 255, 255), self.rect, width=1, border_radius=3)

        worldsize, cellsize, mx, my = self.calc_sizes()

        for y, line in enumerate(self.state.world):
            for x, cell in enumerate(line):
                if cell.type == gamestate.CellType.EMPTY:
                    continue
                rect = pygame.Rect(
                    mx + x * cellsize + cellsize * 0.05,
                    my + y * cellsize + cellsize * 0.05,
                    cellsize * 0.9, cellsize * 0.9)
                if cell.revealed == 1 or (cell.revealed == 0 and self.see_all):
                    pygame.draw.rect(
                        s, (0, 70, 231), rect, width=0, border_radius=3)
                    img = cell.get_img()
                    img = pygame.transform.scale(
                        img, (cellsize * 0.7, cellsize * 0.7))
                    s.blit(
                        img,
                        (rect.x + cellsize * 0.1, rect.y + cellsize * 0.1))
                elif cell.revealed == 0:
                    pygame.draw.rect(
                        s, (0, 45, 150), rect, width=0, border_radius=3)
                else:
                    if cell.revealed < 0.5:
                        progress = 1 - cell.revealed / 0.5
                        color = (0, 45, 150)
                    else:
                        progress = (cell.revealed - 0.5) / 0.5
                        color = (0, 70, 231)
                    rect = pygame.Rect(
                        mx + x * cellsize + cellsize * 0.05
                        + cellsize * 0.45 * (1 - progress),
                        my + y * cellsize + cellsize * 0.05,
                        cellsize * 0.9 * progress, cellsize * 0.9)
                    pygame.draw.rect(
                        s, color, rect, width=0, border_radius=3)
                    if cell.revealed >= 0.5:
                        img = cell.get_img()
                        img = pygame.transform.scale(
                            img, (cellsize * 0.7 * progress, cellsize * 0.7))
                        s.blit(
                            img,
                            (rect.x + rect.w * 0.1, rect.y + cellsize * 0.1))

        # GameState update
        selected_cards = self.state.get_selected_cards()

        if self.state.current_player is not None:
            if self.state.move_state == MoveState.SELECTING_CARDS:
                if (gamestate.CellType.POSTMAN
                        in self.state.current_player.inventory):
                    target_cards = 2
                else:
                    target_cards = 1
                if len(selected_cards) == target_cards:
                    if target_cards == 1:
                        self.state.pick_card(*selected_cards[0])
                    else:
                        self.state.move_state = MoveState.PICKING_CARD

    def on_clicked(self, event):
        worldsize, cellsize, mx, my = self.calc_sizes()

        if self.state.move_state == MoveState.INSPECTOR_EFFECT_LOSS:
            self.state.next_player()
            return

        cx = math.floor((event.x + self.rect.x - mx) / cellsize)
        cy = math.floor((event.y + self.rect.y - my) / cellsize)
        if cy >= 0 and cy < len(self.state.world):
            if cx >= 0 and cx < len(self.state.world[cy]):
                self.on_card_clicked(cx, cy)

    def on_card_clicked(self, cx, cy):
        if self.state.world[cy][cx].type == gamestate.CellType.EMPTY:
            return

        if self.state.get_cards_revealing():
            return

        if self.state.move_state == MoveState.SELECTING_CARDS:
            self.state.world[cy][cx].target_revealed = True

            if self.state.world[cy][cx].revealed == 1:
                self.state.pick_card(cx, cy)

        if self.state.move_state == MoveState.PICKING_CARD:
            if self.state.world[cy][cx].revealed == 1:
                self.state.pick_card(cx, cy)
