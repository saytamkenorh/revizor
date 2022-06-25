import pygame

import sprites
import gamestate
import scenes
import data


TAKE_BTN_TEXTS = {
    gamestate.CellType.MONEY: "Vzít",
    gamestate.CellType.INSPECTOR: "Uplatit ({0})",
    gamestate.CellType.WIFE: "Uplatit ({0})",
    gamestate.CellType.POSTMAN: "Uplatit ({0})",
    gamestate.CellType.SCHOOL_INSPECTOR: "Uplatit ({0})",
    gamestate.CellType.JUDGE: "Uplatit ({0})",
    gamestate.CellType.YEOMEN: "Uplatit ({0})",
}


CANCEL_BTN_TEXTS = {
    gamestate.CellType.MONEY: "Nevzít",
    gamestate.CellType.INSPECTOR: "Nic mu nedat",
    gamestate.CellType.WIFE: "Nechat být",
    gamestate.CellType.POSTMAN: "Nechat být",
    gamestate.CellType.SCHOOL_INSPECTOR: "Nechat být",
    gamestate.CellType.JUDGE: "Nechat být",
    gamestate.CellType.YEOMEN: "Nechat být",
}


class CardDialog(sprites.Widget):
    WIDTH = 500
    HEIGHT = 500
    state: gamestate.GameState
    widgets: sprites.WidgetGroup
    picked_cell: gamestate.Cell
    prev_move_state: gamestate.MoveState

    def __init__(self, x, y, state: gamestate.GameState):
        super().__init__(x, y, CardDialog.WIDTH, CardDialog.HEIGHT)
        self.state = state
        self.prev_move_state = None

        self.widgets = sprites.WidgetGroup()

        self.btn_take = sprites.Button(
            x + CardDialog.WIDTH / 2,
            y + CardDialog.HEIGHT - 90, "")
        self.btn_take.on_clicked_callback = self.on_take
        self.widgets.add(self.btn_take)

        self.btn_cancel = sprites.Button(
            x + CardDialog.WIDTH / 2,
            y + CardDialog.HEIGHT - 40, "")
        self.btn_cancel.on_clicked_callback = self.on_cancel
        self.widgets.add(self.btn_cancel)

    def update(self, fs: scenes.FrameStatus):
        s = fs.surface
        pygame.draw.rect(
            s, (0, 0, 0), self.rect, width=0, border_radius=3)
        pygame.draw.rect(
            s, (255, 255, 255), self.rect, width=3, border_radius=3)

        if self.state.move_state == gamestate.MoveState.INSPECTOR_EFFECT:
            img = gamestate.get_type_image(gamestate.CellType.INSPECTOR)
        else:
            img = self.picked_cell.get_img()
        img = pygame.transform.scale(
            img, (100, 100))
        fs.surface.blit(
            img,
            (self.rect.x + CardDialog.WIDTH / 2 - 50, self.rect.y + 10))

        text_x = self.rect.x + 10
        text_y = self.rect.y + 120

        if self.state.move_state == gamestate.MoveState.INSPECTOR_EFFECT:
            self.update_inspector_effect(fs, text_x, text_y)
        else:
            self.update_card_decision(fs, text_x, text_y)

        self.widgets.update(fs)

    def update_inspector_effect(self, fs, text_x, text_y):
        if self.state.inspector_was_fake:
            text = "Byl to nepravý revizor."
            text_small = "Nic se neděje."
        else:
            text = "Byl to pravý revizor."
            text_small = "Ztrácíte peníze."
        fs.surface.blit(
            data.FONT.render(text, True, (255, 255, 255)),
            (text_x, text_y))
        text_y += data.FONT.get_linesize()
        fs.surface.blit(
            data.TEXT_FONT.render(text_small, True, (255, 255, 255)),
            (text_x, text_y))

    def update_card_decision(self, fs, text_x, text_y):
        if self.picked_cell is None:
            return

        fs.surface.blit(
            data.FONT.render(self.picked_cell.get_name(),
                             True, (255, 255, 255)), (text_x, text_y))
        text_y += data.FONT.get_linesize()

        font = data.TEXT_FONT
        for line in self.picked_cell.get_description().splitlines():
            fs.surface.blit(
                font.render(line, True, (255, 255, 255)), (text_x, text_y))
            text_y += font.get_linesize()

    def update_always(self, fs):
        if self.prev_move_state != self.state.move_state:
            self.move_state_changed()

    def move_state_changed(self):
        self.visible = (
            self.state.move_state == gamestate.MoveState.CARD_DECISION
            or self.state.move_state == gamestate.MoveState.INSPECTOR_EFFECT)
        if not self.visible:
            self.picked_cell = None

        self.picked_cell = self.state.get_picked_cell()
        if self.picked_cell is not None:
            if self.state.move_state == gamestate.MoveState.CARD_DECISION:
                self.btn_take.visible = True
                self.btn_take.set_text(
                    TAKE_BTN_TEXTS[self.picked_cell.type].format(
                        self.picked_cell.price))
                if self.picked_cell.type != gamestate.CellType.MONEY:
                    self.btn_take.active = (
                        self.state.current_player.money
                        >= self.picked_cell.price
                        and self.picked_cell.type
                        not in self.state.current_player.inventory)
                else:
                    self.btn_take.active = True
                self.btn_cancel.visible = True
                self.btn_cancel.set_text(
                    CANCEL_BTN_TEXTS[self.picked_cell.type])
            elif self.state.move_state == gamestate.MoveState.INSPECTOR_EFFECT:
                self.btn_take.visible = False
                self.btn_cancel.visible = True
                self.btn_cancel.set_text(
                    "Budiž")

    def on_take(self):
        self.state.take_picked_cell()

    def on_cancel(self):
        if self.state.move_state == gamestate.MoveState.INSPECTOR_EFFECT:
            self.state.next_player()
            return
        self.state.cancel_picked_cell()
