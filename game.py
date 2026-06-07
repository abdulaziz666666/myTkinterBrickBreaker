
# .أنوه أن اللعبة قد لا تكون معيارًا لتقييم التنظيم فيها

from tkinter import Tk, Canvas, Label, Button, Toplevel, PhotoImage, Entry
from random import randint, choices
from tkinter.messagebox import showerror


width = 600
height = 400

BLOCK_WIDTH = 50
BLOCK_HEIGHT = 30
GAP = 10
blocksNumber = 10
rowsNumber = 3

HEXADECIMALS = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
               'a', 'b', 'c', 'd', 'e', 'f']
DELAY = 50
gameover = False
score = 0
lives = 3


def movePlayerPad(key):
    if gameover:
        return 
    
    rectX1 = canvas.coords(playerPad)[0]
    rectX2 = canvas.coords(playerPad)[2]

    if key.char == 'd' and rectX2 < width:
        canvas.move(playerPad, 20, 0)
    if key.char == 'a' and rectX1 > 0:
        canvas.move(playerPad, -20, 0)

    

def destroyCollidedBlock(yVelocity):
    global blocks, gameover, score
    
    collisionsWithBall = list(canvas.find_overlapping(*canvas.coords(ball)))

    if len(collisionsWithBall) > 1 and playerPad not in collisionsWithBall:
        collisionsWithBall.remove(ball)
        collidedBlock = collisionsWithBall[0]
        blocks.remove(collidedBlock)
        canvas.delete(collidedBlock)

        # print(blocks)
        # print(len(blocks))

        if not blocks:
            canvas.destroy()
            Label(gameWindow, text='!لقد فزت',
                  fg="#1B8B5C", font=('', 16, 'bold')).pack(expand=True, fill='both', padx=200, pady=100)
            gameover = True
            return 0 
        
        if yVelocity > 0:
            yVelocity += 1
        else:
            yVelocity -= 1

        score += 1
        scoreLabel.config(text=str(score))

        _ = randint(1, 10)
        return -yVelocity if _ > 4 else yVelocity
    else:
        return yVelocity

def spawnBall(yVelocity):
    global ball

    ball = canvas.create_oval(10,
                              height-10,
                              40,
                              height-40,
                              fill='red')
    return (10, -abs(yVelocity)) # x, y (velocity)

def ballMovementLogic(xVelocity = 10, yVelocity = -10):
    global gameover, lives

    if gameover:
        return
    else:
        ballCoords = canvas.coords(ball)
        x1, y1, x2, y2 = [round(v) for v in ballCoords]

        if x2 > width or x1 < 0:
            xVelocity = -xVelocity

        if y1 < 0:
            yVelocity = abs(yVelocity)
            if yVelocity < 20: yVelocity += 3

        
        if y2 > height:
            lives -= 1
            livesLabel.config(text=f'{str(lives)} :المحاولات')

            if lives < 1:
                canvas.destroy()
                Label(gameWindow, text='!لقد خسرت',
                      fg='red', font=('', 16, 'bold')).pack(expand=True, fill='both', padx=200, pady=100)
                gameover = True
                return
            else:
                canvas.delete(ball)
                xVelocity, yVelocity = spawnBall(yVelocity)


        if yVelocity > 0 and ball in canvas.find_overlapping(*canvas.coords(playerPad)):
            yVelocity = -abs(yVelocity)

        canvas.move(ball, xVelocity, yVelocity)
        yVelocity = destroyCollidedBlock(yVelocity)
        canvas.after(DELAY, lambda: ballMovementLogic(xVelocity, yVelocity))

def generateBlocks():
    global blocks

    blocks = []
    
    blockY = 10
    for row in range(rowsNumber):
        blockX = 10
        for i in range(blocksNumber):
            color = '#' + ''.join(choices(HEXADECIMALS, k=6))
            blocks.append(canvas.create_rectangle(blockX,
                                                blockY,
                                                blockX + BLOCK_WIDTH,
                                                blockY + BLOCK_HEIGHT,
                                                fill=color))
            blockX += BLOCK_WIDTH + GAP

        blockY += BLOCK_HEIGHT + GAP

def play():
    global gameWindow, playerPad, ball, scoreLabel, livesLabel, canvas, gameover, score, lives

    score = 0
    lives = 3
    gameover = False

    gameWindow = Toplevel(window, width=width, height=height)
    gameWindow.resizable(False, False)

    canvas = Canvas(gameWindow, width=width, height=height, bg='black')
    canvas.pack()

    playerPad = canvas.create_rectangle(width/2 - 50,
                                height-30,
                                width/2 + 50,
                                height-10,
                                fill='white')

    ball = canvas.create_oval(10,
                            height-10,
                            40,
                            height-40,
                            fill='red')
    
    scoreLabel = Label(gameWindow, text=str(score), bg='black', fg='white', font=('', 16, 'bold'))
    livesLabel = Label(gameWindow, text=f'{str(lives)} :المحاولات', bg='black', fg='white', font=('', 16, 'bold'))

    scoreLabel.pack(expand=True, fill='both')
    livesLabel.pack(expand=True, fill='both')

    generateBlocks()
    ballMovementLogic()

    gameWindow.focus()
    gameWindow.bind('<Key>', movePlayerPad)
    gameWindow.bind('<Destroy>', lambda _: playBtn.config(state='normal'))

    playBtn.config(state='disabled')

def checkValuesValidaty(*args: int):
    '''
    should be ordered that way:
        0. width
        1. height
        2. blocksNumber 
        3. rowsNumber
    '''
    horizontalSpaceNeeded = GAP + (BLOCK_WIDTH + GAP) * args[2] 
    verticalSpaceNeeded = GAP + (BLOCK_HEIGHT + GAP) * args[3] 

    if horizontalSpaceNeeded >= args[0] + 20 or verticalSpaceNeeded >= args[1] // 2:
        showerror('خطأ', 'عرض/طول لوحة اللعب غير مناسب\nغير بعض القيم، كالطول والعرض، أو عدد المستطيلات والصفوف')
        return False

                        #  25 >= args[2] >= 10, # checked before
                        #  6 >= args[3] >= 3]  # checked before
    # print(validValuesRanges)
    validValuesRanges = [1000 >= args[0] >= 600, 600 >= args[1] >= 400]
    valuesAreValid = all(validValuesRanges)

    if valuesAreValid:
        return True
    else:
        showerror('خطأ', 'يجب إدخال قيم معقولة ومتناسبة')
        return False

def saveSettings(*args):
    global settingsWindow, width, height, blocksNumber, rowsNumber

    try:
        args = [int(arg) for arg in args]
    except ValueError:
        showerror('خطأ', 'يجب إدخال القيم على صورة أعداد صحيحة فقط')
    else:
        if checkValuesValidaty(*args):
            width, height, blocksNumber, rowsNumber = args    
            settingsWindow.destroy()

def openSettings():
    global blocksNumber, rowsNumber, settingsWindow

    settingsWindow = Toplevel(window)
    settingsWindow.title('الإعدادات')
    settingsWindow.config(bg='black')
    settingsWindow.minsize(250, 300)
    settingsWindow.maxsize(250, 300)

    settingsList = {('عرض لوحة اللعب', width): Entry(settingsWindow, justify='center'),
                    ('طول لوحة اللعب', height): Entry(settingsWindow, justify='center'),
                    ('عدد المربعات لكل صف', blocksNumber): Entry(settingsWindow, justify='center'),
                    ('عدد الصفوف', rowsNumber): Entry(settingsWindow, justify='center')}
    
    for item in settingsList.items():
        Label(settingsWindow, text=item[0][0], bg='black', fg='lightblue').pack(padx=20, pady=5)
        item[1].pack(padx=20, pady=5)
        item[1].insert(0, str(item[0][1]))

    saveBtn = Button(settingsWindow, text='حفظ', bg='black', fg='lightblue', relief='sunken',
                     command=lambda: saveSettings(*[e.get() for e in settingsList.values()]))
    saveBtn.pack(expand=True, fill='both', pady=(10, 0), ipady=10)

    settingsBtn.config(state='disabled')
    settingsWindow.bind('<Destroy>', lambda _: settingsBtn.config(state='normal'))
    
# def f():
#     blocksNumber = (width - ((width//50)*10))//50 - 2
#     print(f'{blocksNumber=}')

window = Tk()
window.title('مُدَمِّر المُستَطِيلات')
window.config(bg='black')
window.resizable(False, False)

hasTitleImage = True
try:
    titleImage = PhotoImage(file='title.png')
except Exception as e:
    titleImageLabel = Label(window, text='مُدَمِّر المُستَطِيلات',
                             fg='lightblue', font=('', 24, 'bold'))
    hasTitleImage = False
    print(e)
else:
    titleImageLabel = Label(window, bg='black', image=titleImage, bd=0)

playBtn = Button(window, text='العب', font=('', 16, 'bold'),
                  bg='black', fg='lightblue', relief='sunken',
                  command=play)

settingsBtn = Button(window, text='إعدادات اللعبة', font=('', 16, 'bold'),
                  bg='black', fg='lightblue', relief='sunken', bd=0,
                  command=openSettings)
if hasTitleImage:
    titleImageLabel.pack(expand=True, fill='x')
else:
    titleImageLabel.pack(ipadx=100, ipady=50)

playBtn.pack(expand=True, fill='x', ipady=20)
settingsBtn.pack(expand=True, fill='x', ipady=20)


window.mainloop()