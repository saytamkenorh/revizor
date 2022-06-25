import pygame
import pygame.locals as pygl

import scenes
import sprites
import data
import gamestate

from gamestate import MoveState


class GameScene(scenes.Scene):
    widgets: sprites.WidgetGroup
    card_dialog: sprites.CardDialog
    state: gamestate.GameState
    ww: sprites.WorldWidget

    cheat_code: str
    cheat_time: int
    cheats_enabled: bool
    CHEAT_RESET_TIME = 10000

    game_end_text: str
    game_end_text_blick: float
    game_end_show_time: float

    def __init__(self, scene_status: scenes.SceneStatus, players: int):
        super().__init__(scene_status)
        self.cheat_code = ""
        self.cheat_time = GameScene.CHEAT_RESET_TIME
        self.cheats_enabled = False
        self.game_end_text = None
        self.game_end_text_blick = 0
        self.game_end_show_time = 0

        self.widgets = sprites.WidgetGroup()
        self.state = gamestate.GameState()
        self.state.reset(
            [f"Hráč {n}" for n in range(1, players + 1)])

        for n, player in enumerate(self.state.players):
            pw = sprites.PlayerWidget(5, n * 150 + 5, player, self.state)
            self.widgets.add(pw)

        w, h = self.scene_status.get_screen_size()
        ww_x, ww_y, ww_w, ww_h = (110, 5, w - 115, h - 10)
        self.ww = sprites.WorldWidget(ww_x, ww_y, ww_w, ww_h, self.state)
        self.widgets.add(self.ww)

        self.card_dialog = sprites.CardDialog(
            ww_x + ww_w / 2 - sprites.CardDialog.WIDTH / 2,
            ww_y + ww_h / 2 - sprites.CardDialog.HEIGHT / 2, self.state)
        self.widgets.add(self.card_dialog)

    def render(self, fs: scenes.FrameStatus):
        self.state.update(fs.clock.get_time() / 1000)
        self.widgets.update(fs)

        for e in fs.events:
            if e.type == pygl.KEYDOWN:
                if e.key == pygl.K_SEMICOLON:
                    self.cheat_time = 0
                    self.cheat_code = ""
                elif e.key == pygl.K_RETURN:
                    self.cheat()
                elif e.unicode.isalpha():
                    if self.cheat_time < GameScene.CHEAT_RESET_TIME:
                        self.cheat_code += e.unicode
                        print(self.cheat_code)
            if e.type == pygl.MOUSEBUTTONUP and self.game_end_show_time >= 1.0:
                if self.state.move_state == MoveState.GAME_END:
                    self.scene_status.set_scene("menu")
        self.cheat_time = min(
            GameScene.CHEAT_RESET_TIME + 1,
            self.cheat_time + fs.clock.get_time())

        # Messages
        def render_msg(msgy, text: str, title: str = "") -> int:
            w, h = self.scene_status.get_screen_size()
            start_x = 115
            end_x = w - 10
            center_x = start_x + (end_x - start_x) / 2

            lines = text.splitlines()
            height = len(lines) * data.TEXT_FONT.get_linesize() + 20
            if title != "":
                height += data.FONT.get_linesize()
            rect = pygame.Rect(start_x, msgy, end_x - start_x, height)
            pygame.draw.rect(
                fs.surface, (0, 0, 0),
                rect,
                width=0, border_radius=3)
            pygame.draw.rect(
                fs.surface, (255, 255, 255),
                rect,
                width=3, border_radius=3)

            msgy += 10
            if title != "":
                tw, th = data.FONT.size(title)
                fs.surface.blit(
                    data.FONT.render(
                        title, True,
                        (255, 255, 255)), (center_x - tw / 2, msgy))
                msgy += data.FONT.get_linesize()

            linesize = data.TEXT_FONT.get_linesize()
            for i, line in enumerate(lines):
                tw, th = data.TEXT_FONT.size(line)
                fs.surface.blit(
                    data.TEXT_FONT.render(
                        line, True,
                        (255, 255, 255)), (center_x - tw / 2, msgy))
                msgy += linesize

            msgy += 10
            return msgy

        msgy = 10
        if self.state.move_state == MoveState.YOEMEN_EFFECT:
            msgy = render_msg(msgy, "Vyberte hráče k pozdržení")
        elif self.state.move_state == MoveState.INSPECTOR_EFFECT_LOSS:
            msgy = render_msg(msgy, """Ve městě se objevil inspektor
a školní inspektor Vám to
u něj zcela pokazil, a proto prohráváte.""", "Prohra")
        elif self.state.move_state == MoveState.GAME_END:
            msgy = render_msg(msgy, self.get_end_game_text(fs), "Konec hry")
            self.game_end_text_blick += fs.clock.get_time() / 1000
            while self.game_end_text_blick > 1.0:
                self.game_end_text_blick -= 1.0
            self.game_end_show_time = min(
                self.game_end_show_time + fs.clock.get_time() / 1000 / 8, 1.0)

    def get_end_game_text(self, fs: scenes.FrameStatus) -> str:
        if self.game_end_text is None:
            lines = ["Pořadí:"]

            winners = list(
                filter(lambda p: p.win_order > 0, self.state.players))
            others = list(
                filter(lambda p: p.win_order == 0 and p.loss_order == 0,
                       self.state.players))
            losers = list(
                filter(lambda p: p.loss_order > 0, self.state.players))

            winners.sort(key=lambda p: p.win_order)
            others.sort(key=lambda p: p.money)
            losers.sort(key=lambda p: p.loss_order, reverse=True)
            for n, p in enumerate(winners + others + losers):
                lines.append(f"{n + 1}. místo: {p.name}")

            lines.append("")
            lines.append("{0}")
            lines.append("  ")
            self.game_end_text = "\n".join(lines)

        return self.game_end_text.format(
            "" if self.game_end_text_blick <= 0.5
            or self.game_end_show_time < 1.0
            else "Pokračujte kliknutím")

    def cheat(self):
        if self.cheat_code == "bingchilling":
            self.state.current_player.money += 750
            self.cheat_code = ""
            self.cheats_enabled = True

        if self.cheat_code == "seecards":
            self.ww.see_all = True

        if self.cheat_code == "cheat":
            import webbrowser
            webbrowser.open(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0, True)

        characters = [
            str(i).replace("CellType.", "").casefold()
            for i in list(gamestate.CellType)]
        if self.cheat_code.casefold() in characters:
            character = gamestate.CellType[self.cheat_code.upper()]
            if character not in self.state.current_player.inventory:
                self.state.current_player.inventory.append(character)
