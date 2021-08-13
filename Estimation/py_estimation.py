import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *

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
            pos = maximum-1
        else:
            pos -= 1
        return pos
    
    def update_pos_backwards(self, maximum, pos):
        if pos == maximum-1:
            pos = 0
        else:
            pos += 1
        return pos
    
    def reverse_score(self, current, last_add):
        return current - last_add


class Button:
    def __init__(self, text, pos, size, bg, fg, val, font=30):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        self.bwidth, self.bheight = size
        self.val = val
        self.text_str = text
        self.fg = fg
        self.bg = bg
        self.set_text(self.text_str, bg, fg)
 
    def set_text(self, text, bg, fg):
        self.text = self.font.render(text, 1, pygame.Color(fg))
        self.size = (self.bwidth, self.bheight)
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
        self.tsize = self.text.get_size()
        self.surface.blit(self.text, (self.size[0]/2-self.tsize[0]/2, self.size[1]/2-self.tsize[1]/2))
 
    def show(self):
        display.blit(self.surface, (self.x, self.y))
 
    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if self.rect.collidepoint((x, y)):
                self.animate_click()
                return self.val
    
    def animate_click(self):
        self.set_text(self.text_str, self.bg, self.bg)
        self.show()
        pygame.display.update()
        time.sleep(0.1)
        self.set_text(self.text_str, self.bg, self.fg)
        self.show()
        pygame.display.update()


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color("DarkGreen")
        self.text = text
        self.font = pygame.font.SysFont("Arial", 30)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = True
        self.flag = False
        self.top = y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            if self.active:
                self.color = pygame.Color("DarkGreen")
            else:
                self.color = pygame.Color("Red")
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.flag = True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, "Black")

    def draw(self, tflash):
        display.fill("White", (0, self.top, display.get_width(), display.get_height()-self.top))
        txt_size = self.txt_surface.get_size()
        xpos = self.rect.x + self.rect.width//2 - txt_size[0]//2
        ypos = self.rect.y + 3
        display.blit(self.txt_surface, (xpos, ypos))
        pygame.draw.rect(display, self.color, self.rect, 2)
        if tflash == True and self.active == True:
            tbar = pygame.Rect(xpos+txt_size[0], ypos, 2, txt_size[1])
            pygame.draw.rect(display, "Black", tbar)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def initialise_game():
    set_list = True
    message = "Enter the number of players: "
    no_players = int(setup_screen(message, "nums"))

    options = []
    opts_path = resource_path("estimation_options.txt")
    with open("estimation_options.txt", "r") as f:
        for line in f:
            line = line.strip('\n')
            try:
                num = int(line[0])
            except:
                continue
            if num == no_players:
                line = line[1:]
                line = line.strip().split()
                for i in range(0, len(line)):
                    try:
                        line[i] = int(line[i])
                    except:
                        pass
                options.append(line)
    
    if len(options) == 0:
        message = "Rounds and Trumps Must be Set Manually"
        x = setup_screen(message, 'noops')
    else:
        message = []
        message.append("Choose the rounds from the options (the game can be ended any time)")
        message.append("Alternatively edit the file estimation_options.txt to add a new game")
        o_list = []
        for k in range(0, len(options), 2):
            message.append(f"{int(k/2)+1}    {options[k]}")
            o_list.append(int(k/2)+1)
        message.append(f"{len(o_list)+1}    Set Rounds Manually")
        o_list.append(len(o_list)+1)
        message.append(f"Choose an option 1 - {str(len(o_list))}:")
        while True:
            opt = int(setup_screen(message, "rounds"))
            if opt in o_list:
                break

    try:
        round_list = options[2*(opt-1)]
        trump_list = options[2*(opt-1) + 1]
        Nround = len(round_list)
    except:
        round_list = []
        trump_list = []
        Nround = 1000
        set_list = False


    players = []

    for i in range(0, no_players):
        if i == 0:
            message = "Enter first dealers name: "
        else:
            message = "Enter name of next player to the left: "
        name = setup_screen(message, "names")
        players.append(Player(name, i))

    for p in players:
        p.pos = p.update_pos(no_players, p.pos)
    players.sort(key=lambda p: p.pos)

    os.system('clear')
    return players, trump_list, round_list, set_list, Nround


def get_button_input(buttons):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            res = None
            for b in buttons:
                res = b.click(event)
                if res != None:
                    return res


def get_text_input(input_boxes):
    done = False
    tbar = False
    c = 0
    clock = pygame.time.Clock()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            for box in input_boxes:
                box.handle_event(event)
                if box.flag == True:
                    return box.text

        for box in input_boxes:
            box.draw(tbar)

        pygame.display.flip()
        clock.tick(30)
        c += 1
        if c == 20:
            tbar = not tbar
            c = 0


def go_back_round(players, r):
    no_players = len(players)
    if r == 0:
        opt = 1
    else:
        while True:
            opt = goback_screen()
            if opt == 1 or opt == 2:
                break 

    if opt == 1:
        return players, r
    for p in players:
        p.total_score = p.reverse_score(p.total_score, p.score_record[-1]-p.score_record[-2])
        p.score_record.pop(-1)
        p.guess_record.pop(-1)
        p.pos = p.update_pos_backwards(no_players, p.pos)
    players.sort(key=lambda p: p.pos)
    return players, r-1
    

def take_guesses(players, tricks, banner, r, Nrounds, gb_button):
    total_called = -1
    count = 1
    for p in players:
        p.guess = ''
        p.tricks_won = ''

    for i in range(len(players)):
        p = players[i]
        c_go = -1
        if i == len(players)-1:
            c_go = tricks - total_called
        message = f"Choose the Guess for {p.name}:"
        buttons = create_buttons(tricks, c_go, gb_button)
        draw_screen(players, banner, message, buttons, p.name, total_called, -1, Nrounds, r, tricks)
        g = get_button_input(buttons)

        if g == "goback":
            return players, True
        else:
            g = int(g)

        if r>2:
            if g==p.guess_record[-1] and g==p.guess_record[-2] and g==p.guess_record[-3]:
                message = str(p.name)+' has gone '+str(g)+' 3 times. Enter again to override or choose new: '
                draw_screen(players, banner, message, buttons, p.name, total_called, -1, Nrounds, r, tricks)
                g = get_button_input(buttons)

                if g == "goback":
                    return players, True
                else:
                    g = int(g)
                    
        total_called = max(total_called+g, g)
        p.guess = g
        p.guess_record.append(g)
        count += 1

    return players, False


def take_scores(players, tricks, banner, tc, r, Nrounds, gb_button):
    no_players = len(players)
    test = False
    mstart = ""
    while test == False:
        for p in players:
            p.tricks_won = ''
        total_won = -1
        for i in range(len(players)):
            p = players[i]

            message = f"{mstart}Choose the Score for {p.name}:"
            buttons = create_buttons(tricks, -1, gb_button)
            draw_screen(players, banner, message, buttons, p.name, tc, total_won, Nrounds, r, tricks)
            won = get_button_input(buttons)

            if won == "goback":
                return players, True
            else:
                won = int(won)
                
            total_won = max(total_won+won, won)
            p.tricks_won = won
        if total_won == tricks:
            test = True
        else:
            mstart = "Reenter Scores - Incorrect No. Tricks. "

    for p in players:
        p.total_score = p.update_score(p.guess, p.tricks_won, p.total_score)
        p.pos = p.update_pos(no_players, p.pos)
        p.score_record.append(p.total_score)
    players.sort(key=lambda p: p.pos)

    return players, False


def ask_next_round():
    message = "Continue With Next Round?"
    font30 = pygame.font.SysFont('Arial', 30)
    
    box_size = (display.get_width()//2, display.get_height()//2)
    box_pos = (box_size[0]//2, box_size[1]//2-15)
    pygame.draw.rect(display, pygame.Color(default_col), box_pos+box_size, border_radius=10)

    msg = font30.render(message, 1, pygame.Color("White"))
    msg_size = msg.get_size()
    display.blit(msg, (box_size[0] - msg_size[0]/2, box_size[1]//2 + 10))

    bc = Button("Yes", (box_size[0]-110, box_size[1]//2+90), (60, 40), "Gray", pygame.Color("Black"), True, 25)
    bs = Button("No", (box_size[0]+50, box_size[1]//2+90), (60, 40), "Gray", pygame.Color("Black"), False, 25)

    bc.show()
    bs.show()

    pygame.display.flip()

    return get_button_input([bc, bs])


def create_buttons(tricks, c_go, gb_button):
    buttons = []
    Nb = tricks + 1
    ypos = 100
    for i in range(Nb):
        if i == c_go:
            continue
        xpos = 10 + i*60
        buttons.append(Button(str(i), (xpos,ypos), (50,30), pygame.Color(default_col), "white", i))
    buttons.append(gb_button)
    return buttons


def draw_screen(players, banner, message, buttons, nd, tc, tot_won, Nround, r, Ntricks):
    # Banner: 40
    # Message: 60
    # Buttons: 50
    # Table Head: 40
    # Players: 40 * N
    # Total Called: 60
    # YSize = 250 + 40 * N

    font30 = pygame.font.SysFont('Arial', 30)
    font27 = pygame.font.SysFont('Arial', 27)
    font25 = pygame.font.SysFont('Arial', 25)
    font25B = pygame.font.SysFont('Arial', 25, bold=True)
    font20 = pygame.font.SysFont('Arial', 20)

    display.fill("White")

    # Banner
    Bsurface = pygame.Surface((900,40))
    Bsurface.fill(pygame.Color(default_col))
    display.blit(Bsurface, (0,0))
    banner_text = font25B.render(banner, 1, pygame.Color("White"))
    display.blit(banner_text, (10,6))

    # Message
    if len(message) <= 62:
        message_text = font27.render(message, 1, pygame.Color("Black"))
    else:
        message_text = font20.render(message, 1, pygame.Color("Black"))
    display.blit(message_text, (10,55))

    for b in buttons:
        b.show()
    
    h1 = font30.render("Player", 1, pygame.Color("Black"))
    h2 = font30.render("Guess", 1, pygame.Color("Black"))
    h3 = font30.render("Tricks Won", 1, pygame.Color("Black"))
    h4 = font30.render("Total Score", 1, pygame.Color("Black"))
    hy = 150
    display.blit(h1, (10, hy))
    display.blit(h2, (180, hy))
    display.blit(h3, (330, hy))
    display.blit(h4, (530, hy))
    bar = pygame.Surface((870, 3))
    bar.fill(pygame.Color(default_col))
    display.blit(bar, (10, hy+35))
    if "Final" in message:
        players.sort(key=lambda p: p.total_score, reverse=True)
    else:
        players.sort(key=lambda p: p.init_pos)
    ypos = 190
    for i in range(len(players)):
        ypos = 195 + i*40
        p = players[i]
        name = font25.render(str(p.name), 1, pygame.Color("Black"))
        g = font25.render(str(p.guess), 1, pygame.Color("Black"))
        tw = font25.render(str(p.tricks_won), 1, pygame.Color("Black"))
        ts = font25.render(str(p.total_score), 1, pygame.Color("Black"))

        if p.name == nd:
            psurface = pygame.Surface((872, 30))
            psurface.fill(pygame.Color(default_bar))
            display.blit(psurface, (8, ypos))

        display.blit(name, (10, ypos))
        display.blit(g, (180, ypos))
        display.blit(tw, (330, ypos))
        display.blit(ts, (530, ypos))

    # Total Called
    if tc >= 0:
        ou = "Over"
        v = tc - Ntricks
        if v < 0:
            ou = "Under"
        elif v == 0:
            ou = "Diff"
            v = "No"
        try:
            v = abs(v)
        except:
            pass
        if tot_won < 0:
            m = "Total Called: {:>2}       {:>2} {}".format(tc, v, ou)
        else:
            m = "Total Called: {:>2}       {:>2} {}       Total Scored: {}".format(tc, v, ou, tot_won)
        ctext = font25.render(m, 1, pygame.Color("Black"))
        display.blit(ctext, (10, ypos+50))
    
    ntot = Nround
    if ntot > 50:
        ntot = "na"
    round_text = font25.render(f"{r+1}/{ntot}", 1, "Black")
    rsize = round_text.get_size()
    display.blit(round_text, (880-rsize[0], ypos+50))

    pygame.display.update()
    players.sort(key=lambda p: p.pos)


def setup_screen(message, mode):
    font30 = pygame.font.SysFont('Arial', 30)
    font25 = pygame.font.SysFont('Arial', 25)
    font20 = pygame.font.SysFont('Arial', 20)

    display.fill("White")

    if mode == "nums" or mode == "names" or mode == "noops":
        message_text = font30.render(message, 1, pygame.Color("Black"))
        msize = message_text.get_size()
        display.blit(message_text, (450-msize[0]/2,10))
    elif mode == "rounds":
        for i in range(len(message)):
            message_text = font20.render(message[i], 1, pygame.Color("Black"))
            msize = message_text.get_size()
            display.blit(message_text, (10,10+i*25))

    input_boxes = []
    if mode == "nums" or mode == "names":
        input_boxes.append(InputBox(300, 100, 300, 40))
    elif mode == "rounds":
        input_boxes.append(InputBox(300, 340, 300, 40))
    elif mode == "noops":
        b = Button("Ok", (420, 100), (60, 40), pygame.Color(default_col), "White", 1, 25)
        b.show()
        pygame.display.update()
        return get_button_input([b])

    return get_text_input(input_boxes)


def goback_screen():
    font20 = pygame.font.SysFont('Arial', 20)

    m1 = "Choose an option:"
    m2 = "1: Go Back to the start of this round"
    m3 = "2: Go back to the start of the last round"
    msgs = [m1, m2, m3]
    
    box_size = (display.get_width()//2, display.get_height()//2)
    box_pos = (box_size[0]//2, box_size[1]//2-15)
    pygame.draw.rect(display, pygame.Color(default_col), box_pos+box_size, border_radius=10)

    for i in range(len(msgs)):
        message = msgs[i]
        msg = font20.render(message, 1, pygame.Color("White"))
        msg_size = msg.get_size()
        display.blit(msg, (box_size[0] - msg_size[0]/2, box_size[1]//2 + 5 + i*30))

    bc = Button("1", (box_size[0]-70, box_size[1]//2+120), (50, 30), "Grey", "Black", 1, 25)
    bs = Button("2", (box_size[0]+20, box_size[1]//2+120), (50, 30), "Grey", "Black", 2, 25)

    bc.show()
    bs.show()

    pygame.display.update()

    return get_button_input([bc, bs])


def ask_no_tricks():
    display.fill("White")
    msg = "How Many Tricks in This Round?"
    font30 = pygame.font.SysFont('Arial', 30)

    message = font30.render(msg, 1, pygame.Color("Black"))
    msize = message.get_size()
    display.blit(message, (450-msize[0]/2,10))

    input_boxes = []
    input_boxes.append(InputBox(300, 100, 300, 40))

    return get_text_input(input_boxes)


def play_game(players, trump_list, round_list, set_list, Nround, gb_button):
    r = 0
    while r < Nround:
        if set_list == True:
            tricks = round_list[r]
            banner = f"Round: {r+1}    Cards: {tricks}    Trumps: {trump_list[r]}    Dealer: {players[-1].name}"
        else:
            while True:
                try:
                    tricks = int(ask_no_tricks())
                    break
                except:
                    pass
            banner = f"Round: {r+1}    Cards: {tricks}    Dealer: {players[-1].name}"
        
        players, goback = take_guesses(players, tricks, banner, r, Nround, gb_button)
        if goback == True:
            players, r = go_back_round(players, r)
            continue
        
        total_called = 0
        for p in players:
            total_called += p.guess

        players, goback = take_scores(players, tricks, banner, total_called, r, Nround, gb_button)
        if goback == True:
            players, r = go_back_round(players, r)
            continue

        if r < Nround-1:
            if ask_next_round() == False:
                break

        r += 1
    
    draw_screen(players, banner, "Final Scores:", [], p.name, -1, -1, Nround, r, 0)
    return players


def main():
    global default_col
    global default_bar
    default_col = "DarkViolet"
    default_bar = "Lavender"

    os.system('clear')
    pygame.init()
    global display
    display = pygame.display.set_mode((900, 400))
    pygame.display.set_caption("Estimation Scoresheet")

    players, trump_list, round_list, set_list, Nround = initialise_game()

    display = pygame.display.set_mode((900, 240 + 40*len(players)))
    gb_button = Button("Go Back", (750, 5), (125, 30), pygame.Color("Gray"), "black", "goback", 20)

    players = play_game(players, trump_list, round_list, set_list, Nround, gb_button)

    plot_list = np.arange(0, len(players[0].score_record), 1)
    for p in players:
        plt.plot(plot_list, p.score_record, label=p.name)
    plt.xlabel('Round')
    plt.ylabel('Score')
    plt.legend()
    plt.show()

    pygame.quit()


if __name__ == '__main__':
    main()