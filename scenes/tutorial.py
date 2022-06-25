import pygame
import pygame.locals as pygl

import scenes
import data

PAGES = [
    """
Vítejte ve hře Revizor!
Revizor je hra inspirovaná stejnoujmennou divadelní hrou
od Nikolaje Nikolaje Vasiljeviče Gogola.
Jedná se o hru pro 2 - 4 hráčů, kteří
se vžijí do role hejtama, jenž musí
uplatit celé město.
    """,
    """
Po spuštění hry se objeví hrací plocha s kartami.
Hráči se střídají a klikáním vybírají karty na hrací ploše.
Před každým tahem hráč získá 40 peněz.""",
    """
Druhy karet:
Peníze
- Hráči se přičte daný objem peněz
- Karta po otočení mizí
Karta postavy
- Ve hře je celkem 5 různých postav
- Při vybraní této karty lze postavu za peníze "uplatit" a
    zařadit si postavu do sbírky, karta poté zmizí
- Druhá možnost je postavu nechat být, karta se otočí zpět
- Cílem je hry postupně uplatit všech 5 postav
    """,
    """
Každá z postav má speciální schopnost,
o které si lze přečíst po otočení postavy.
Schopnost se uplaťňuje po uplacení postavy.
Může se jednat o jednorázovou či trvalou schopnost.
    """,
    """
Karta revizora
- Revizor může být pravý nebo falešný, to však není na kartě znát
- Při otočení této karty dostane hráč na výběr dvě možnosti
- Hráč může revizora uplatit, poté pokračuje další hráč
- Hráč neuplatí revizora:
    - Falešný revizor -> pokračuje další hráč
    - Pravý revizor -> hráč ztrácí až 600 peněz
      (má-lí méně než 600, ztratí všechny)
- Po výběru jedné ze dvou možnosti se hráč dozví pravost revizora
- Karta poté zmizí
    """,
    """
Konec hry
- Hráč vyhraje, když uplatí všech 5 postav
- Díky jedné z postav je také možné prohrát
- Hra se hraje, dokud ve hře nezbyde jen 1 hráč
    - Ostatní vyhrají nebo prohrají
    """
]


class TutorialScene(scenes.Scene):
    page: int
    text: str
    anim_state: float  # Number of revealed chars
    blick_state: float

    w: int
    h: int
    f: pygame.font.Font

    def __init__(self, scene_status: scenes.SceneStatus):
        super().__init__(scene_status)

        self.w, self.h = scene_status.get_screen_size()
        self.f = data.TEXT_FONT
        self.linesize = self.f.get_linesize() * 1.25

        self.load_page(0)

    def load_page(self, num: int):
        self.page = num
        self.anim_state = 0
        self.blick_state = 0

        self.text = PAGES[num]
        lines = self.text.splitlines()

        self.width = max([self.f.size(line)[0] for line in lines])
        self.height = self.linesize * len(lines)

    def render(self, fs: scenes.FrameStatus):
        for event in fs.events:
            if event.type == pygl.MOUSEBUTTONDOWN:
                if self.anim_state >= len(self.text):
                    if self.page + 1 < len(PAGES):
                        self.load_page(self.page + 1)
                    else:
                        self.scene_status.set_scene("menu")
                else:
                    self.anim_state = len(self.text)

        self.anim_state = min(
            len(self.text),
            self.anim_state + fs.clock.get_time() / 1000 * 30)
        self.blick_state = self.blick_state + fs.clock.get_time() / 1000
        while self.blick_state >= 1.0:
            self.blick_state -= 1.0

        if self.anim_state >= len(self.text):
            if self.blick_state <= 0.5:
                ctext = "Pokračujte kliknutím"
                w, h = self.f.size(ctext)
                fs.surface.blit(
                    self.f.render(ctext, True, (255, 255, 255)),
                    (self.w / 2 - w / 2, self.h - 50))

        x = self.w / 2 - self.width / 2
        y = self.h / 2 - self.height / 2

        for line in self.text[:round(self.anim_state)].splitlines():
            fs.surface.blit(
                self.f.render(line, True, (255, 255, 255)), (x, y))

            y += self.linesize
