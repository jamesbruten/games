import asyncio
from nicegui import ui

DEBUG = False


class Player:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.init_pos = pos
        self.total_score = 0
        self.guess = None
        self.tricks_won = None
        self.score_record = [0]
        self.guess_record = []

    def update_score(self, tricks_won):
        inc = tricks_won
        if self.guess == tricks_won:
            inc += 10
        self.total_score += inc
        self.score_record.append(self.total_score)
        self.tricks_won = tricks_won

    def revert_score(self):
        tricks_won = self.tricks_won
        self.score_record = self.score_record[:-1]
        self.total_score = self.score_record[-1]
        self.tricks_won = None
        return tricks_won

    def update_pos(self, maximum):
        if self.pos == 0:
            self.pos = maximum - 1
        else:
            self.pos -= 1


class Game:
    def __init__(self):
        self.no_players = None
        self.players = []
        self.init_order = []
        self.rounds = None
        self.round_ind = None
        self.counter = 0
        self.max_score = 0
        self.min_score = 0

    def update_player_pos(self):
        for p in self.players:
            p.update_pos(self.no_players)
        self.players.sort(key=lambda p: p.pos)

    def reset_players(self):
        for p in self.players:
            p.tricks_won = None
            p.guess = None


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


async def wait_for_click(elements, go_back):
    if type(elements) is not list:
        elements = [elements]
    if go_back is not None:
        elements.append(go_back)
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
        ui.chip(
            "Enter Number of Players:", color="purple-7", text_color="white"
        )
        ui.toggle(list(round_options.keys())).bind_value(game, "no_players")
        continue_button = ui.button("Continue")
    await continue_button.clicked()
    container.clear()
    return game


async def get_player_names(game):
    if DEBUG:
        for i, p in enumerate(["a", "b", "c", "d"]):
            game.players.append(Player(p, i))
            game.init_order.append(p)
        return game
    container = ui.column()
    with container:
        ui.chip(
            "Enter the players in order from left to right, "
            "starting with the 1st dealer",
            color="purple-7",
            text_color="white",
        )
        txt_boxes = []
        for i in range(game.no_players):
            if i == 0:
                txt_boxes.append(
                    ui.input(label=f"Player {i+1}").props("autofocus")
                )
            else:
                txt_boxes.append(ui.input(label=f"Player {i+1}"))

        continue_button = ui.button("Continue")
        await continue_button.clicked()
        for i, txt_box in enumerate(txt_boxes):
            game.players.append(Player(txt_box.value.capitalize().strip(), i))
            game.init_order.append(txt_box.value.capitalize().strip())
    container.clear()
    return game


async def choose_rounds(game, round_options):
    if DEBUG:
        game.rounds = round_options[4][0]
        return game
    container = ui.column()
    with container:
        radio_opts = []
        for i, opt in enumerate(round_options[game.no_players]):
            radio_opts.append(f"{i+1} - " + ", ".join(str(x) for x in opt[0]))
        ui.radio(radio_opts).bind_value(game, "round_ind").props("vertical")
        continue_button = ui.button("Choose this set of rounds")
    await continue_button.clicked()
    game.round_ind = int(game.round_ind.split("-")[0].strip())
    game.rounds = round_options[game.no_players][game.round_ind - 1]
    container.clear()
    return game


def print_banner(cards, trumps, players, rnum, tot, called=None):

    ui.chip(f"Round: {rnum}/{tot}", color="purple-7", text_color="white")
    ui.chip(f"Cards: {cards}", color="cyan-7", text_color="white")
    if trumps in "HD":
        c = "red"
    else:
        c = "black"
    ui.chip(f"Trumps: {trumps}", color=c, text_color="white")
    ui.chip(f"Dealer: {players[-1].name}", color="amber-7", text_color="white")
    if called is not None:
        diff = cards - called
        if diff < 0:
            ui.chip(
                f"Over: {diff*-1}", color="deep-orange-7", text_color="white"
            )
        else:
            ui.chip(f"Under: {diff}", color="deep-orange-7", text_color="white")


async def initialise_game(round_options):

    game = Game()

    game = await get_no_players(game, round_options)
    game = await get_player_names(game)
    game = await choose_rounds(game, round_options)
    game.update_player_pos()

    return game


def draw_table(players, order, highlight="", mode=None):

    data = []
    columns = [
        {"name": "name", "label": "Name", "field": "name", "required": True},
        {"name": "guess", "label": "Guess", "field": "guess"},
        {"name": "won", "label": "Won", "field": "won"},
        {"name": "score", "label": "Score", "field": "score", "required": True},
    ]
    for name in order:
        for player in players:
            if player.name != name:
                continue
            row = {
                "name": name,
                "score": player.total_score,
            }
            if mode != "guess" or player.guess is not None:
                row["guess"] = player.guess
            if player.tricks_won is not None:
                row["won"] = player.tricks_won
            data.append(row)
    table = ui.table(
        rows=data,
        columns=columns,
        column_defaults={"headerClasses": "text-bold text-purple-7"},
    )
    table.add_slot(
        "body-cell",
        rf"""
            <q-td
                :props="props"
                :class="(props.row.name=='{highlight}')?
                    'bg-purple-2 text-black':'bg-white text-black'"
            >
                {{{{props.value}}}}
            </q-td>
            """,
    )


def draw_score_buttons(
    ncards, record, unavailable=999, min_score=0, chosen=None
):
    with ui.button_group().props("color='blue-8'"):
        btns = []
        for opt in range(min_score, ncards + 1):
            if opt == unavailable:
                btn = ui.button(
                    opt,
                    color="red-500",
                    on_click=lambda opt=opt: ui.notify(
                        f"Pick another option than {opt} you prick",
                        color="red-500",
                    ).props("color='blue-8'"),
                )
            else:
                props = "color='blue-8'"
                if chosen is not None and opt == chosen:
                    props += ' text-color="amber-14"'
                btn = ui.button(opt, on_click=lambda i=opt: record(i)).props(
                    props
                )
                btns.append(btn)
    return btns


def plot_scores(game, rnum):
    with ui.card():
        with ui.matplotlib(figsize=(6, 4)).figure as fig:
            x_data = list(range(rnum))
            ax = fig.gca()
            ax.set_xlim(0, len(game.rounds[0]))
            ax.set_ylabel("Score")
            ax.set_xlabel("Round")
            for name in game.init_order:
                for player in game.players:
                    if player.name != name:
                        continue
                    y_data = player.score_record[:rnum]
                    ax.plot(x_data, y_data, "-", label=player.name)
            ax.legend()


async def take_guesses(cards, game, rnum):
    page = ui.column()
    total_called = 0
    unavailable = 999
    with page:
        game.counter = 0
        while game.counter < len(game.players):
            player = game.players[game.counter]

            def record_option(val):
                player.guess = val

            def step_back(num=2):
                game.players[game.counter - int(num / 2)].guess = None
                game.counter -= num

            if game.counter == game.no_players - 1:
                unavailable = cards - total_called
            with ui.card().classes("w-full"):
                with ui.row().classes("w-full"):
                    ui.chip(
                        f"Enter Guess for {player.name}:",
                        color="blue-8",
                        text_color="white",
                    )
                    go_back = None
                    if game.counter > 0:
                        ui.space()
                        go_back = ui.button(
                            "Revert",
                            icon="arrow_back",
                            color="grey",
                            on_click=lambda: step_back(),
                        ).props("rounded")
                score_buttons = draw_score_buttons(
                    cards, record_option, unavailable=unavailable
                )

            with ui.row():
                draw_table(
                    game.players, game.init_order, player.name, mode="guess"
                )
                plot_scores(game, rnum)

            await wait_for_click(score_buttons, go_back)

            if game.counter == game.no_players - 1:
                page.clear()
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full"):
                        cont = ui.button("Continue to Scoring?", color="green")
                        ui.space()
                        go_back = ui.button(
                            "Go Back",
                            color="grey",
                            on_click=lambda: step_back(1),
                        ).props("rounded")
                with ui.row():
                    draw_table(game.players, game.init_order, "")
                    plot_scores(game, rnum)
                await wait_for_click(cont, go_back)

            try:
                total_called += player.guess
            except TypeError:
                pass
            page.clear()
            game.counter += 1

    page.clear()
    return game, total_called


async def take_scores(cards, game, rnum):
    page = ui.column()
    game.max_score = cards
    game.min_score = 0
    with page:
        game.counter = 0
        while game.counter < game.no_players:
            player = game.players[game.counter]

            def record_option(val):
                player.update_score(val)

            def step_back(num=2, revert=True):
                won = game.players[game.counter - int(num / 2)].revert_score()
                if revert:
                    game.max_score += won
                game.min_score = 0
                game.counter -= num

            with ui.card().classes("w-full"):
                with ui.row().classes("w-full"):
                    ui.chip(
                        f"Enter Number of Tricks won by {player.name}:",
                        color="blue-8",
                        text_color="white",
                    )
                    go_back = None
                    if game.counter > 0:
                        ui.space()
                        go_back = ui.button(
                            "Go Back",
                            color="grey",
                            on_click=lambda: step_back(),
                        ).props("rounded")
                if game.counter == game.no_players - 1:
                    game.min_score = game.max_score
                score_buttons = draw_score_buttons(
                    game.max_score,
                    record_option,
                    min_score=game.min_score,
                    chosen=player.guess,
                )

            with ui.row():
                draw_table(
                    game.players, game.init_order, player.name, mode="score"
                )
                plot_scores(game, rnum)

            await wait_for_click(score_buttons, go_back)

            if game.counter == game.no_players - 1:
                page.clear()
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full"):
                        if rnum == len(game.rounds[0]):
                            txt = "End the game?"
                        else:
                            txt = "Finish this round?"
                        cont = ui.button(txt, color="green")
                        ui.space()
                        go_back = ui.button(
                            "Go Back",
                            color="grey",
                            on_click=lambda: step_back(1, False),
                        ).props("rounded")
                with ui.row():
                    draw_table(game.players, game.init_order, "")
                    plot_scores(game, rnum + 1)
                await wait_for_click(cont, go_back)

            try:
                game.max_score -= player.tricks_won
            except TypeError:
                pass
            page.clear()
            game.counter += 1
    return game


async def main(round_options):

    game = await initialise_game(round_options)

    rnum = 1
    page = ui.column()
    for cards, trumps in zip(game.rounds[0], game.rounds[1]):
        with page:
            banner_page = ui.row()
            with banner_page:
                print_banner(
                    cards, trumps, game.players, rnum, len(game.rounds[0])
                )
            page2 = ui.column()
            with page2:
                game, total_called = await take_guesses(cards, game, rnum)
                page2.clear()
            banner_page.clear()
            with banner_page:
                print_banner(
                    cards,
                    trumps,
                    game.players,
                    rnum,
                    len(game.rounds[0]),
                    total_called,
                )
            with page2:
                game = await take_scores(cards, game, rnum)
                page2.clear()
            game.update_player_pos()
            game.reset_players()
            rnum += 1
            banner_page.clear()
            page.clear()


round_options = read_round_options()

ui.timer(interval=1, callback=lambda: main(round_options), once=True)
ui.run()
