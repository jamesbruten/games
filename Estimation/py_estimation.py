import asyncio
from nicegui import Tailwind, ui
from time import sleep

DEBUG = True


class Player:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.init_pos = pos
        self.total_score = 0
        self.guess = 0
        self.tricks_won = 0
        self.score_record = [0]
        self.guess_record = []

    def update_score(self, guess, tricks_won, total_score):
        if guess == tricks_won:
            total_score += 10 + tricks_won
        else:
            total_score += tricks_won
        return total_score

    def update_pos(self, maximum, pos):
        if pos == 0:
            pos = maximum - 1
        else:
            pos -= 1
        return pos

    def update_pos_backwards(self, maximum, pos):
        if pos == maximum - 1:
            pos = 0
        else:
            pos += 1
        return pos

    def reverse_score(self, current, last_add):
        return current - last_add


class Game:
    def __init__(self):
        self.no_players = None
        self.players = []
        self.rounds = None
        self.round_ind = None

    def update_player_pos(self):
        for p in self.players:
            p.pos = p.update_pos(self.no_players, p.pos)
        self.players.sort(key=lambda p: p.pos)


def read_round_options():
    round_options = {}
    with open("estimation_options.txt", "r") as f:
        opt = []
        for line in f:
            line = line.strip("\n")
            try:
                num = int(line[0])
            except:
                continue
            line = line[1:]
            line = line.strip().split()
            for i in range(0, len(line)):
                try:
                    line[i] = int(line[i])
                except:
                    pass
            opt.append(line)
            if len(opt) == 2:
                if num not in round_options:
                    round_options[num] = []
                round_options[num].append(opt)
                opt = []

    return round_options


async def wait_for_click(elements):
    if type(elements) is not list:
        elements = [elements]
    continue_event = asyncio.Event()
    for element in elements:
        element.on("click", continue_event.set)
    await continue_event.wait()


async def wait_for_enter(element):
    continue_event = asyncio.Event()
    element.on("keydown.enter", continue_event.set)
    await continue_event.wait()


async def get_no_players(game, round_options):
    if DEBUG:
        game.no_players = 4
        return game
    container = ui.column()
    with container:
        ui.label("Enter Number of Players:")
        ui.toggle(list(round_options.keys())).bind_value(game, "no_players")
        continue_button = ui.button("Continue")
    await continue_button.clicked()
    container.clear()
    return game


async def get_player_names(game):
    if DEBUG:
        for i, p in enumerate(["a", "b", "c", "d"]):
            game.players.append(Player(p, i))
        return game
    container = ui.column()
    with container:
        ui.label(
            "Enter the players in order from left to right, "
            "starting with the 1st dealer"
        )
        txt_boxes = []
        for i in range(game.no_players):
            txt_boxes.append(ui.input(label=f"Player {i+1}"))

        continue_button = ui.button("Continue")
        await continue_button.clicked()
        for i, txt_box in enumerate(txt_boxes):
            game.players.append(Player(txt_box.value.capitalize().strip(), i))
    container.clear()
    return game


async def choose_rounds(game, round_options):
    if DEBUG:
        game.rounds = round_options[4][0]
        return game
    container = ui.column()
    with container:
        avail = []
        with ui.card():
            for i, opt in enumerate(round_options[game.no_players]):
                ui.label(f"{i+1} - {', '.join(str(x) for x in opt[0])}")
                avail.append(i + 1)
        ui.label("Select an option from above")
        ui.toggle(avail).bind_value(game, "round_ind")
        continue_button = ui.button("Continue")
    await continue_button.clicked()
    game.rounds = round_options[game.no_players][game.round_ind - 1]
    container.clear()
    return game


def print_banner(cards, trumps, players):
    banner = f"Trumps: {trumps}    Cards: {cards}    Dealer: {players[-1].name}"
    ui.label(banner).tailwind.background_color('purple-300')



async def initialise_game(round_options):

    game = Game()

    game = await get_no_players(game, round_options)
    game = await get_player_names(game)
    game = await choose_rounds(game, round_options)
    game.update_player_pos()

    return game


async def take_guesses(cards, trumps, game):
    page = ui.column()
    total_called = 0
    with page:
        print_banner(cards, trumps, game.players)
        options = [x for x in range(cards+1)]
        for i, player in enumerate(game.players):
            if i == game.no_players - 1:
                options.remove(cards - total_called)

    return game



async def main(round_options):

    game = await initialise_game(round_options)

    for cards, trumps in zip(game.rounds[0], game.rounds[1]):
        game = await take_guesses(cards, trumps, game)


round_options = read_round_options()

ui.timer(interval=1, callback=lambda: main(round_options), once=True)
ui.run()
