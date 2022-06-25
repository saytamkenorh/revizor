from enum import Enum, auto
from typing import Union
import random
import math
import pygame

import data


class CellType(Enum):
    MONEY = auto(),
    # Player can either bribe him or risk loosing all the money
    INSPECTOR = auto(),
    # Player's next turn is random
    WIFE = auto(),
    # Player can look at up to two cards and take one of them
    POSTMAN = auto(),
    # If an inspector catches the player then player quits the game
    SCHOOL_INSPECTOR = auto(),
    # Sells dogs to the player, takes 1/4 of income
    JUDGE = auto()
    # Player can choose other player who looses half of money
    YEOMEN = auto()
    EMPTY = auto()


class MoveState(Enum):
    SELECTING_CARDS = auto()  # Selecting card to reveal
    PICKING_CARD = auto()  # Choose one card
    CARD_DECISION = auto()
    INSPECTOR_EFFECT = auto()
    INSPECTOR_EFFECT_LOSS = auto()
    WIFE_EFFECT = auto()
    YOEMEN_EFFECT = auto()
    GAME_END = auto()


class Player:
    name: str
    money: int
    blocked_moves: int
    loss_order: int
    win_order: int
    wife_effect: bool
    inventory: list[CellType]

    def __init__(self, name: str):
        self.name = name
        self.money = 0
        self.inventory = []
        self.blocked_moves = 0
        self.wife_effect = False
        self.loss_order = 0
        self.win_order = 0


IMG_NAMES = {
    CellType.MONEY: "coin_large.png",
    CellType.INSPECTOR: "inspector.png",
    CellType.WIFE: "wife.png",
    CellType.POSTMAN: "postman.png",
    CellType.SCHOOL_INSPECTOR: "school_inspector.png",
    CellType.JUDGE: "judge.png",
    CellType.YEOMEN: "yeomen.png"
}


def get_type_image(t: CellType) -> pygame.Surface:
    return data.get_img(IMG_NAMES[t], 1)


CELL_NAMES = {
    CellType.MONEY: "Peníze",
    CellType.INSPECTOR: "Inspektor",
    CellType.WIFE: "Manželka",
    CellType.POSTMAN: "Poštmistr",
    CellType.SCHOOL_INSPECTOR: "Školní inspektor",
    CellType.JUDGE: "Soudce",
    CellType.YEOMEN: "Bočinskij a dobčinskij"
}


CELL_DESCRIPTIONS = {
    CellType.MONEY: """Můžeš získat {0} peněz.
Samozřejmě poctivým způsobem.""",
    CellType.INSPECTOR: """Do města údajně přijel inspektor.
Lze jej uplatit a zachránit si krk.
Mohl by to ale být falešný inspektor.
V takovém případě je možné nic mu nedat.
Pokud to ale bude pravý inspektor,
ztratíte až 600 pěnez
(dle Vašeho bohatství) jako pokutu.""",
    CellType.WIFE: """Vaše manželka Vám neustále mluví
do Vašich věcí. V jednom dalším tahu
po uplacení Vám tak před tahem otočí
jednu kartu. Tu si poté musíte vzít.""",
    CellType.POSTMAN: """Poštmistr otevírá veškerou korespondenci,
která mu projde pod rukama.
Podplatíte-li si ho, bude si moci
vždy otočit až dvě karty
a vybrat si jednu z nich.""",
    CellType.SCHOOL_INSPECTOR: """Školní inspektor má strach
z důležitých úředních osobností.
Může tak vytvořit trapnou situaci.
Pokud si jej podplatíte, získate si ho,
avšak pokud přijde do města
jakýkoliv inspektor,
hra pro Vás ihned skončí.""",
    CellType.JUDGE: """Soudce pravidelně vyžaduje
úplatky ve štěňatech,
která jsou jeho vášní.
Bude-li na Vaší straně, vezme čtvrtinu
z každého Vašeho budoucího příjmu.""",
    CellType.YEOMEN: """Oba tito zemané
jsou známí roznašeči zpráv.
Pokud si je podplatíte,
za odměnu roznesou o vybraném
soupeři drb. Bude si tak muset spravit
reputaci a nebude hrát 1 tah.""",
}


class Cell:
    type: CellType
    price: int
    revealed: float
    target_revealed: bool

    def __init__(self, type: CellType, price: int):
        self.type = type
        self.price = price
        self.revealed = 0
        self.target_revealed = False

    def get_img(self) -> pygame.Surface:
        return data.get_img(IMG_NAMES[self.type], 1)

    def get_description(self) -> str:
        return CELL_DESCRIPTIONS[self.type].format(self.price)

    def get_name(self) -> str:
        return CELL_NAMES[self.type]


class GameState:
    world: list[list[Cell]]
    players: list[Player]
    current_player: Player
    move_state: MoveState
    picked_card: Union[None, tuple[int, int]]
    inspector_was_fake: bool

    def __init__(self):
        self.players = []
        self.world = []
        self.picked_card = None
        self.inspector_was_fake = False
        self.reset([])

    def reset(self, players: list[str]):
        self.players.clear()
        for pname in players:
            self.players.append(Player(pname))
        self.current_player = (
            self.players[-1] if len(self.players) > 0 else None)
        if len(self.players) > 0:
            self.next_player()
        self.move_state = MoveState.SELECTING_CARDS

        self.world.clear()
        nplayers = len(players)
        wsize = math.ceil(
            math.sqrt((2 * nplayers)
                      + nplayers * 5))
        for y in range(wsize):
            self.world.append(
                [Cell(CellType.MONEY, 200) for x in range(wsize)])

        def find_free_spot() -> tuple[int, int]:
            while True:
                x = random.randint(0, wsize - 1)
                y = random.randint(0, wsize - 1)
                if self.world[y][x].type == CellType.MONEY:
                    return (x, y)

        def add_cell(cell: Cell):
            x, y = find_free_spot()
            self.world[y][x] = cell

        for n in range(nplayers):
            add_cell(Cell(CellType.INSPECTOR, 300))

            # Money sum: 750
            add_cell(Cell(CellType.JUDGE, 50))
            add_cell(Cell(CellType.POSTMAN, 250))
            add_cell(Cell(CellType.SCHOOL_INSPECTOR, 100))
            add_cell(Cell(CellType.WIFE, 150))
            add_cell(Cell(CellType.YEOMEN, 200))

    def update(self, delta: float):
        for line in self.world:
            for cell in line:
                if cell.revealed < 1.0 and cell.target_revealed:
                    cell.revealed = min(1.0, cell.revealed + delta)
                if cell.revealed > 0 and (not cell.target_revealed):
                    cell.revealed = max(0, cell.revealed - delta)

    def get_selected_cards(self) -> list[tuple[int, int]]:
        selected_cards = []
        for y, line in enumerate(self.world):
            for x, cell in enumerate(line):
                if cell.revealed == 1:
                    selected_cards.append((x, y))
        return selected_cards

    def get_cards_revealing(self) -> bool:
        for y, line in enumerate(self.world):
            for x, cell in enumerate(line):
                if cell.revealed > 0 and cell.revealed < 1:
                    return True
        return False

    def get_picked_cell(self) -> Union[None, Cell]:
        if self.picked_card is None:
            return None
        x, y = self.picked_card
        return self.world[y][x]

    def pick_card(self, cx, cy):
        assert self.world[cy][cx].revealed == 1
        assert (self.move_state == MoveState.SELECTING_CARDS
                or self.move_state == MoveState.PICKING_CARD)

        self.move_state = MoveState.CARD_DECISION
        self.picked_card = (cx, cy)

        for y, line in enumerate(self.world):
            for x, cell in enumerate(line):
                if cx == x and cy == y:
                    continue
                if cell.target_revealed:
                    cell.target_revealed = False

        if self.get_picked_cell().type == CellType.INSPECTOR:
            if CellType.SCHOOL_INSPECTOR in self.current_player.inventory:
                self.lose_player(self.current_player)
                self.world[cy][cx] = Cell(CellType.EMPTY, 0)
                self.move_state = MoveState.INSPECTOR_EFFECT_LOSS

    def lose_player(self, player: Player):
        if player.loss_order != 0:
            return
        player.loss_order = (
            max([p.loss_order for p in self.players]) + 1)

    def win_player(self, player: Player):
        if player.win_order != 0:
            return
        player.win_order = (
            max([p.win_order for p in self.players]) + 1)

    def take_picked_cell(self):
        picked_cell = self.get_picked_cell()
        if picked_cell is None:
            return
        px, py = self.picked_card

        if picked_cell.type == CellType.MONEY:
            self.current_player.money += picked_cell.price
            if CellType.JUDGE in self.current_player.inventory:
                self.current_player.money -= picked_cell.price / 4
        else:
            assert picked_cell.type not in self.current_player.inventory
            if self.current_player.money < picked_cell.price:
                return
            self.current_player.money -= picked_cell.price
            if picked_cell.type != CellType.INSPECTOR:
                self.current_player.inventory.append(picked_cell.type)

        self.world[py][px] = Cell(CellType.EMPTY, 0)

        if picked_cell.type == CellType.WIFE:
            self.current_player.wife_effect = True
        if picked_cell.type == CellType.YEOMEN:
            self.move_state = MoveState.YOEMEN_EFFECT
        else:
            self.next_player()

    def cancel_picked_cell(self):
        picked_cell = self.get_picked_cell()
        if picked_cell is None:
            return
        px, py = self.picked_card

        if picked_cell.type == CellType.INSPECTOR:
            self.world[py][px] = Cell(CellType.EMPTY, 0)
            is_fake = random.randint(1, 100) <= 50
            self.inspector_was_fake = is_fake
            if not is_fake:
                self.current_player.money = max(
                    0, self.current_player.money - 600)
            self.move_state = MoveState.INSPECTOR_EFFECT
            return

        picked_cell.target_revealed = False
        self.next_player()

    def next_player(self):
        if self.check_end_game():
            self.move_state = MoveState.GAME_END
            return

        self.move_state = MoveState.SELECTING_CARDS

        def next_player_index(i) -> int:
            return (i + 1) % len(self.players)

        index = next_player_index(self.players.index(self.current_player))
        while (self.players[index].loss_order != 0
               or self.players[index].win_order != 0
               or self.players[index].blocked_moves > 0):
            if self.players[index].blocked_moves > 0:
                self.players[index].blocked_moves -= 1
            index = next_player_index(index)

        self.current_player = self.players[index]
        if CellType.JUDGE in self.current_player.inventory:
            self.current_player.money += 40 * 0.75
        else:
            self.current_player.money += 40

        if self.current_player.wife_effect:
            self.current_player.wife_effect = False
            while True:
                y = random.randint(0, len(self.world) - 1)
                x = random.randint(0, len(self.world[y]) - 1)
                if self.world[y][x].type != CellType.EMPTY:
                    self.world[y][x].target_revealed = True
                    self.world[y][x].revealed = 0.001
                    self.move_state = MoveState.PICKING_CARD
                    break

    def check_end_game(self) -> bool:
        for p in self.players:
            if len(p.inventory) >= 5:
                self.win_player(p)

        players_out = len(
            list(filter(lambda p: p.loss_order > 0 or p.win_order > 0,
                        self.players)))
        if players_out >= len(self.players) - 1:
            return True

        return False
