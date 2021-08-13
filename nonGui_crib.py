import sys
import os
import matplotlib.pyplot as plt
import random
from copy import deepcopy

class Player:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.score = 0


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
    Nplayers = int(input("Enter the Number of Players: "))
    players = []
    for i in range(0, Nplayers):
        name = input("Enter Player Names in order of player to the left: ")
        players.append(Player(name, i))

    print("Choose the first dealer, 1 -", Nplayers+1)
    for i in range(0, Nplayers+1):
        if i != Nplayers:
            print(i+1, "-", players[i].name)
        else:
            print(i+1, "- Choose Randomly")
    dealer_pos = int(input("Option: "))
    if dealer_pos == Nplayers+1:
        dealer_pos = random.randint(0, Nplayers-1)

    for p in players:
        s = Nplayers - dealer_pos
        p.pos += s
        p.pos %= Nplayers
    players.sort(key=lambda p: p.pos)

    return players


def play_game(players):
    winning_score = 121
    while True:
        print("\n\nBox: ", players[-1].name, "\n\n")
        print("Enter Number Pegged (enter q when finished):")
        check = True
        while check:
            for p in players:
                n = str(p.name) + ': '
                inp = input(n)
                try:
                    p.score += int(inp)
                    plot_graph(deepcopy(players))
                except:
                    if inp == 'q':
                        check = False
                    break
                if p.score >= winning_score:
                    n = '\n\n' + str(p.name) + ' won'
                    print(n)
                    return players
        players.sort(key=lambda p: p.score)
        os.system("clear")
        for p in players:
            n = str(p.name) + ': ' + str(p.score)
            print(n)
        players.sort(key=lambda p: p.pos)
        print("\n\nBox: ", players[-1].name, "\n\n")
        print("Enter Number in Hand:")
        for p in players:
            n = str(p.name)+': '
            pegs = int(input(n))
            if pegs == 31:
                print("\nLucky Bastard\n")
            p.score += pegs
            plot_graph(deepcopy(players))
            if p.score >= winning_score:
                n = '\n\n' + str(p.name) + ' won'
                print(n)
                return players
        n = str(players[-1].name)+' (Box): '
        players[-1].score += int(input(n))
        plot_graph(deepcopy(players))
        players.sort(key=lambda p: p.score)
        os.system("clear")
        for p in players:
            n = str(p.name) + ': ' + str(p.score)
            print(n)

        for p in players:
            p.pos += 1
            p.pos %= len(players)
        players.sort(key=lambda p: p.pos)

global winning_score
winning_score = 121

players = initialise_game()
os.system("clear")

for p in players:
    n = str(p.name) + ': ' + str(p.score)
    print(n)
plot_graph(deepcopy(players))
    
players = play_game(players)
plot_graph(deepcopy(players), True)