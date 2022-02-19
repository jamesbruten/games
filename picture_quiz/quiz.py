import os
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tkinter as tk
from functools import partial
from PIL import ImageTk, Image

def show_image(ind, t):
    available[ind] = False
    ind -= 1
    path = pics + dirs[ind] + '/' + dirs[ind][2:]
    for j in range(2, -1, -1):
        try:
            fname = path + str(j) + '.jpg'
            img = mpimg.imread(fname)
        except:
            try:
                fname = path + str(j) + '.png'
                img = mpimg.imread(fname)
            except:
                try:
                    fname = path + str(j) + '.webp'
                    img = mpimg.imread(fname)    
                except:
                    fname = path + str(j) + '.jpeg'
                    img = mpimg.imread(fname)    
        fig = plt.imshow(img)
        plt.title('Option: {}   Points: {}'.format(ind+1, j+1))
        plt.axis('off')
        plt.show()
    window.destroy()

def resize_image(bgPath):
    img = Image.open(bgPath)
    width = 500
    height = 400
    img = img.resize((width, height), Image.ANTIALIAS)
    return img



global dirs, pics, available

try:
    folder = sys.argv[1]
except:
    folder = 'xmas_films'

if folder == 'xmas_films':
    emoji = '🎄'
elif folder == 'musicals':
    emoji = '🎶'
elif folder == 'landmarks':
    emoji = '🏰'
elif folder == 'imdb50':
    emoji = '🎥'
elif folder == 'disney':
    emoji = '🎬'

pics = f'./{folder}/'
dirs = os.listdir(pics)
dirs = sorted(dirs)
for item in dirs:
    try:
        x = int(item[:2])
    except:
        dirs.remove(item)
available = {}
for i in range(1, 13):
    available[i] = True
bgPath = pics + 'background.png'

img = resize_image(bgPath)

while True:
    window = tk.Tk()
    window.geometry("500x400")
    window.title("Quiz")
    my_img = ImageTk.PhotoImage(img)
    bg = tk.Label(window, image = my_img, bd=0)
    bg.place(relx=0, rely=0, anchor="nw")
    bg.lower()
    val = 1
    for i in range(3):
        window.rowconfigure(i, weight=1, minsize=75)
        for j in range(4):
            window.columnconfigure(j, weight=1, minsize=75)
            if available[val]:
                btn = tk.Button(window, borderwidth=0, text=f"{emoji}   {val}   {emoji}", height=2, width=5, relief='flat')
                btn.grid(row=i, column=j)
                btn.bind('<Button-1>', partial(show_image, val))
            val += 1
    window.mainloop()
    if sum(int(x) for x in available.values()) == 0:
        break