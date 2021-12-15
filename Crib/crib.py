import sys
import os
import matplotlib.pyplot as plt
import random
import time
import pygame
from pygame.locals import *

class Player:
    def __init__(self, name, pos, col):
        self.name = name
        self.pos = pos
        self.init_pos = pos
        self.score = 0
        self.score_record = []
        self.col = col


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
            tbar = pygame.Rect(xpos+txt_size[0]+2, ypos, 2, txt_size[1])
            pygame.draw.rect(display, "Black", tbar)


class SelectBox:
    def __init__(self, x, y, w, h, text, beg_ac):
        self.rect = pygame.Rect(x, y, w, h)
        self.active = beg_ac
        if self.active:
            self.color = pygame.Color("DarkGreen")
        else:
            self.color = pygame.Color("Red")
        self.text = text
        self.font = pygame.font.SysFont("Arial", 25)
        self.txt_surface = self.font.render(text, True, self.color)
        self.top = y
    
    def click(self, event, sboxes):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                for s in sboxes:
                    s.active = False
                    s.draw()
                self.active = True
                self.draw()
                pygame.display.flip()
                return self.text
        return None
    
    def draw(self):
        if self.active:
            self.color = pygame.Color("DarkGreen")
        else:
            self.color = pygame.Color("Red")
        self.txt_surface = self.font.render(self.text, True, self.color)
        txt_size = self.txt_surface.get_size()
        xpos = self.rect.x + self.rect.width//2 - txt_size[0]//2
        ypos = self.rect.y + 4
        display.blit(self.txt_surface, (xpos, ypos))
        pygame.draw.rect(display, self.color, self.rect, 2)


def get_button_input(buttons, sboxes=[], name=""):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            res = None
            for s in sboxes:
                temp = s.click(event, sboxes)
                if temp != None:
                    name = temp
            for b in buttons:
                res = b.click(event)
                if res != None:
                    return res, name


def get_text_input(input_boxes):
    done = False
    bar_show = False
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
            box.draw(bar_show)

        pygame.display.flip()
        clock.tick(30)
        c += 1
        if c == 20:
            bar_show = not bar_show
            c = 0


def plot_graph(players, b=False):
    try:
        plt.close()
    except:
        pass
    players.sort(key=lambda p: p.name,)
    fig, ax1 = plt.subplots()
    ax1.set_xlim(0, winning_score+12)
    for i in range(0, len(players)):
        ax1.barh(players[i].name, players[i].score, align='center', label=players[i].name)
        ax1.text(players[i].score + 3, players[i].name, str(players[i].score))
    ax2 = ax1.twinx()
    ax2.axvline(x=winning_score, ls='--', color='black')
    ax2.set_xlim(0, winning_score+12)
    ax2.set_yticks([])
    plt.show(block=b)
    return


def initialise_game():
    message = "Enter the number of players: "
    Nplayers = int(setup_screen(message, "nums"))

    players = []
    colours = ["DarkOrange", "MediumSeaGreen", "DodgerBlue"]
    for i in range(0, Nplayers):
        message = "Enter Player Names in order of player to the left:"
        name = setup_screen(message, "names")
        players.append(Player(name, i, colours[i]))

    message = "Choose the first dealer:"
    dealer_pos = int(setup_screen(message, "dealer", players))
    if dealer_pos == Nplayers+1:
        dealer_pos = random.randint(0, Nplayers-1)

    for p in players:
        s = Nplayers - dealer_pos
        p.pos += s
        p.pos %= Nplayers
    players.sort(key=lambda p: p.pos)

    return players


def setup_screen(message, mode, players=[]):
    font30 = pygame.font.SysFont('Arial', 30)
    font25 = pygame.font.SysFont('Arial', 25)
    font20 = pygame.font.SysFont('Arial', 20)

    display.fill("White")

    if mode == "nums" or mode == "names" or mode == "dealer":
        message_text = font30.render(message, 1, pygame.Color("Black"))
        msize = message_text.get_size()
        display.blit(message_text, (display.get_width()//2-msize[0]/2,10))
    
    input_boxes = []
    if mode == "nums":
        b2 = Button("2", (display.get_width()//2-100, 100), (60,40), default_col, 'White', 2, 25)
        b3 = Button("3", (display.get_width()//2+40, 100), (60,40), default_col, 'White', 3, 25)
        b2.show()
        b3.show()
        pygame.display.update()
        a, b = get_button_input([b2, b3])
        return a
    elif mode == "names":
        input_boxes.append(InputBox(300, 100, 300, 40))
        return get_text_input(input_boxes)
    elif mode == "dealer":
        buttons = []
        ypos = 100
        bw = 110
        bh = 40
        for i in range(len(players)+1):
            try:
                txt = players[i].name
            except:
                txt = "Random"
            if (len(players)==2):
                xpos = display.get_width()//2 - 20 - 1.5*bw
            else:
                xpos = display.get_width()//2 - 30 - 2*bw
            buttons.append(Button(txt, (xpos + i * (bw+20), ypos), (bw,bh), default_col, 'White', i, 25))
        for b in buttons:
            b.show()
        pygame.display.update()
        a, b = get_button_input(buttons)
        return a


def draw_screen(players, last_guess):
    font27 = pygame.font.SysFont('Arial', 27)
    font25 = pygame.font.SysFont('Arial', 25)
    font25B = pygame.font.SysFont('Arial', 25, bold=True)

    display.fill("White")

    # Scores
    box_txt = font25B.render(f"Box: {players[-1].name}", 1, "White")
    players.sort(key=lambda p: p.init_pos)
    score_txt = ""
    for p in players:
        score_txt += "{:<18}".format(str(p.name)+": "+str(p.score))
    Bsurface = pygame.Surface((display.get_width(),40))
    Bsurface.fill(pygame.Color(default_col))
    display.blit(Bsurface, (0,0))
    banner_text = font25B.render(score_txt, 1, pygame.Color("White"))
    bpos = display.get_width() - 20 - box_txt.get_width()
    display.blit(banner_text, (10,6))
    display.blit(box_txt, (bpos,6))

    message = "Choose Player to Enter Score:"
    mtext = font27.render(message, 1, "Black")
    display.blit(mtext, (10, 55))

    rypos = 100
    rh = 40
    rw = 110
    sboxes = []
    if (len(players)==2):
        rxpos = display.get_width()//2 - 10 - rw
    else:
        rxpos = display.get_width()//2 - 20 - 1.5*rw
    for i in range(len(players)):
        p = players[i]
        beg_ac = False
        if last_guess == p.name:
            beg_ac = True
        sboxes.append(SelectBox(rxpos, rypos, rw, rh, p.name, beg_ac))
        sboxes[i].draw()
        rxpos += 20 + rw
    

    cypos = 165
    ch = 40
    width = 0
    for p in players:
        width = max(width, font25.render("{:<12}".format(p.name), 1, p.col).get_width()+10)
    for p in players:
        ntext = "{:<12}".format(p.name)
        ntext = font25.render(ntext, 1, p.col)
        display.blit(ntext, (10, cypos))
        full_width = display.get_width()-width-30
        fill_width = int(full_width * p.score / winning_score)
        outline = pygame.Rect(width+10, cypos, full_width, ch)
        filled = pygame.Rect(width+10, cypos, fill_width, ch)
        pygame.draw.rect(display, p.col, outline, 2)
        pygame.draw.rect(display, p.col, filled)
        cypos += ch+10

    bypos = cypos+30
    bxpos = 10
    bh = 30
    bw = 50
    buttons = []
    for i in range(1, 33):
        if i == 17:
            bypos += bh + 5
            bxpos = 10
        if (i < 32):
            buttons.append(Button(str(i), (bxpos,bypos), (bw,bh), default_col, "White", i))
        else:
            buttons.append(Button("Del", (bxpos,bypos), (bw,bh), default_col, "Gray", "del"))
        bxpos += 60
    
    buttons.append(Button("End Round", (display.get_width()-20-rw, 100), (rw,rh), "Gray", "White", "end", 20))
    
    for b in buttons:
        b.show()
    
    pygame.display.update()
    
    val, name = get_button_input(buttons, sboxes=sboxes, name=last_guess)
    players.sort(key=lambda p: p.pos)
    return val, name


def play_game(players):
    font30 = pygame.font.SysFont('Arial', 50, bold=True)
    while True:
        last_guess = players[0].name
        while True:
            val, name = draw_screen(players, last_guess)
            for i in range(len(players)):
                p = players[i]
                if p.name == name:
                    last_guess = p.name
                    ind = i
                    break
            p = players[ind]
            if val == "end":
                break
            elif val == "del":
                p.score -= p.score_record[-1]
                p.score_record = p.score_record[:-1]
            else:
                p.score += int(val)
                p.score_record.append(int(val))
                if p.score > winning_score:
                    display.fill(default_col)
                    txt = font30.render(f"{p.name} wins!!!", 1, p.col)
                    xpos = display.get_width()//2 - txt.get_width()//2
                    ypos = display.get_height()//4
                    display.blit(txt, (xpos,ypos))
                    pygame.display.update()
                    a, b = get_button_input([])
        for p in players:
            p.pos += 1
            p.pos %= len(players)
        players.sort(key=lambda p: p.pos)


global winning_score
global default_col
global default_bar
winning_score = 121
default_col = "DarkViolet"
default_bar = "Lavender"

pygame.init()
display = pygame.display.set_mode((980, 200))

os.system("clear")

players = initialise_game()

display = pygame.display.set_mode((980, 400+(len(players)-2)*50))
    
play_game(players)