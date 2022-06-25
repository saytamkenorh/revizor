import scenes
import sprites


class SetupScene(scenes.Scene):
    widgets: sprites.WidgetGroup

    w: int
    h: int

    def __init__(self, scene_status: scenes.SceneStatus):
        super().__init__(scene_status)

        self.w, self.h = scene_status.get_screen_size()
        self.widgets = sprites.WidgetGroup()

        title = sprites.Label(
            self.w / 2, self.h / 2 - 100, "Vyberte počet hráčů")
        self.widgets.add(title)

        max_players = 4
        n_buttons = max_players - 1
        btn_width = 100

        for n in range(2, max_players + 1):
            text = str(n)
            btn = sprites.Button(
                self.w / 2
                - (btn_width * n_buttons) / 2
                + btn_width * (n - 2) + btn_width / 2,
                self.h / 2,
                text)

            btn.on_clicked_callback = self.startgame
            btn.on_clicked_callback_data = [n]
            self.widgets.add(btn)

    def startgame(self, players):
        self.scene_status.set_scene("game", players)

    def render(self, fs: scenes.FrameStatus):
        self.widgets.update(fs)
