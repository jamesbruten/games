import os
import sys
import numpy as np
import matplotlib.pyplot as plt

os.system('clear')

class Player:

    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
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



def get_input(message):
    while True:
        inp = input(message)
        if inp == 'goback':
            return 0, True
        try:
            inp = int(inp)
            return inp, False
        except:
            print("Must enter a number")



def go_back_round(players, r):
    no_players = len(players)
    if r == 0:
        opt = 1
    else:
        print("\nChoose an option:")
        print("1:\tGo Back to the start of this round")
        print("2:\tGo back to the start of the last round - this will lose all details of the last round")
        while True:
            opt, f = get_input("Option, 1 or 2: ")
            if opt == 1 or opt == 2:
                break 

    if opt == 1:
        return players, r
    for p in players:
        p.total_score = p.reverse_score(p.total_score, p.score_record[-1]-p.score_record[-2])
        p.score_record.pop(-1)
        p.guess_record.pop(-1)
        p.pos = p.update_pos_backwards(no_players, p.pos)
    return players, r-1
    

def take_guesses(players, tricks):
    total_called = 0
    count = 1
    print("Enter the guesses:")
    check = False
    while check==False:
        for p in players:
            if count == no_players:
                c_go = tricks - total_called
                print('Can\'t Go: ', c_go)
                n = str(p.name) + ': '
                test = False
                while test==False:
                    g, goback = get_input(n)
                    if goback == True:
                        return players, True
                    if r>2:
                        if g==p.guess_record[-1] and g==p.guess_record[-2] and g==p.guess_record[-3]:
                            n = str(p.name)+' has gone '+str(g)+' 3 times\nEnter again to override or choose new: '
                            g, goback = get_input(n)
                            if goback == True:
                                return players, True
                    if g!=c_go:
                        test = True
                    else:
                        print('Can\'t Go: ', c_go)
            else:
                n = str(p.name) + ': '
                g, goback = get_input(n)
                if goback == True:
                    return players, True
                if r>2:
                    if g==p.guess_record[-1] and g==p.guess_record[-2] and g==p.guess_record[-3]:
                        n = str(p.name)+' has gone '+str(g)+' 3 times\nEnter again to override or choose new: '
                        g, goback = get_input(n)
                        if goback == True:
                            return players, True
                        
            total_called += g
            p.guess = g
            count += 1
        cont = input("Are the guesses correct? y/n: ")
        if cont == 'y':
            check = True
            for p in players:
                p.guess_record.append(p.guess)
        elif cont == 'goback':
            return players, True
        else:
            total_called = 0
            count = 1
    print('\nTotal Called: ', total_called, '\n')

    return players, False



def take_scores(players, tricks):
    no_players = len(players)
    print("Enter the number of tricks won:")
    test = False
    while test == False:
        total_won = 0
        for p in players:
            n = str(p.name) + ' (' + str(p.guess) + '): '
            won, goback = get_input(n)
            if goback == True:
                return players, True
            total_won += won
            p.tricks_won = won
        if total_won == tricks:
            test = True
        else:
            print("Incorrect number of tricks entered - reenter tricks won:")
    for p in players:
        p.total_score = p.update_score(p.guess, p.tricks_won, p.total_score)
        p.pos = p.update_pos(no_players, p.pos)
        p.score_record.append(p.total_score)

    return players, False


#########################################################################################################################
#########################################################################################################################


print("During the game enter \'goback\' at any time to return to the start of the current or previous round\n")
set_list = True
no_players = int(input("Enter the number of players: "))

options = []
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

print("\nChoose the rounds from the options (the game can be ended any time)")
print("Alternatively edit the file estimation_options.txt to add a new game\n")
o_list = []
for k in range(0, len(options), 2):
    print(int(k/2)+1, "\t", options[k])
    o_list.append(int(k/2)+1)
print(len(o_list)+1, "\tSet Rounds Manually\n")
o_list.append(len(o_list)+1)
while True:
    n = 'Choose an option 1-' + str(len(o_list)) + ': '
    opt = int(input(n))
    if opt in o_list:
        break

try:
    round_list = options[2*(opt-1)]
    trump_list = options[2*(opt-1) + 1]
    Nround = len(round_list)
    print('')
except:
    print("Both Trumps and Card Numbers must be decided manually\n")
    Nround = 1000
    set_list = False


players = []

for i in range(0, no_players):
    if i == 0:
        name = input("Enter first dealers name: ")
    else:
        name = input("Enter name of next player to the left: ")
    players.append(Player(name, i))

for p in players:
    p.pos = p.update_pos(no_players, p.pos)
players.sort(key=lambda p: p.pos)

os.system('clear')

r = 0
while r < Nround:
    os.system('clear')
    players.sort(key=lambda p: p.total_score, reverse=True)
    for p in players:
        print(p.name, p.total_score)
    print('\n')
    players.sort(key=lambda p: p.pos)

    if set_list == True:
        tricks = round_list[r]
        print('Round: ', r+1, '\tCards: ', tricks, '\tTrumps: ', trump_list[r], '\tDealer: ', players[-1].name, '\n')
    else:
        tricks = int(input('Enter the number of tricks in this round: '))
        print('Round: ', r+1, '\tCards: ', tricks, '\tDealer: ', players[-1].name, '\n')
    
    players, goback = take_guesses(players, tricks)
    if goback == True:
        players, r = go_back_round(players, r)
        continue

    players, goback = take_scores(players, tricks)
    if goback == True:
        players, r = go_back_round(players, r)
        continue

    if r < Nround-1:
        if input("\nContinue game? y/n: ") == 'n':
            break

    r += 1




os.system('clear')
players.sort(key=lambda p: p.total_score, reverse=True)       
print("Final Results:")
for p in players:
    print(p.name, p.total_score)

plot_list = np.arange(0, len(players[0].score_record), 1)
for p in players:
    plt.plot(plot_list, p.score_record, label=p.name)
plt.xlabel('Round')
plt.ylabel('Score')
plt.legend()
plt.show()