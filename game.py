
# .أنوه أن اللعبة قد لا تكون معيارًا لتقييم التنظيم فيها

from tkinter import Tk, Canvas, Label, Button, Toplevel, PhotoImage, Entry, Checkbutton, BooleanVar
from random import randint, choice, choices
from tkinter.messagebox import showerror
from playsound import playsound
from threading import Thread

# Canvas Dimensions
canvas_dimensions = {'width': 600, 'height': 400}

# Blocks Values
GAP = 10
BLOCK_WIDTH = 50
BLOCK_HEIGHT = 30
blocks_data = {'blocks number': 10, 'rows number': 3, 'blocks list': []}

# In-game Variables
gameover = False
score = 0
lives = 3

# Constants
BTN_STYLING_STYLE = {'bg': 'black', 'fg': 'lightblue', 'relief': 'sunken'}
WIN_LOSE_LABEL_STYLE = {'win': {'text': '!لقد فزت', 'fg': '#1B8B5C'},
                             'lose': {'text': '!لقد خسرت', 'fg': 'red'}}
BTN_PACK = {'expand': True, 'fill': 'both', 'ipady': 20}
WIN_LOSE_LABEL_PACK = {'expand': True, 'fill': 'both', 'padx': 200, 'pady': 100}

HEXADECIMALS = '123456789ABCDEF'
DELAY = 50
player_pad_width = 100 # Might be affected by width_factor
PLAYER_PAD_SPEED = 20 # The overall value of player pad speed might be affected by width_factor
MAXIMUM_Y_VELOCITY = 20 # Any value over that isn't capable. Tkinter can't process fast movements


def play_sfx(sfxName: str):
    '''
    It plays sound effects from the folder 'sfx'.
    '''
    try:

        if sfxName == 'lose':
            sfxName = choice(('los', 'lose2', 'lose3'))
        
        playsound(f'sfx/{sfxName}.wav', block=False)

    except Exception as e: # Just to prevent any error from occurrence. Its just a sound effect anyway.
        print(e)

def check(case: str, condition: bool):
    '''
    It returns True if CONDITION so.
    Otherwise, it returns False.\n
    It also style & pack a label with args of CASE from WIN_LOSE_LABEL(STYLE/PACK).
    '''
    if condition:
        Thread(target=lambda: play_sfx(case)).start()
        canvas.destroy()
        Label(game_window, WIN_LOSE_LABEL_STYLE[case], font=('', 16, 'bold')).pack(WIN_LOSE_LABEL_PACK)
        return True
    else:
        return False

def move_player_pad(key):
    '''
    It controls the movement of player's pad (striker)\n
    depending on any keyboard input which's represented
    by key.
    '''
    if gameover:
        return 
    
    pad_x1 = canvas.coords(player_pad)[0]
    pad_x2 = canvas.coords(player_pad)[2]

    if key.char == 'd' and pad_x2 < canvas_dimensions['width']:
        canvas.move(player_pad, PLAYER_PAD_SPEED * width_factor, 0)
    if key.char == 'a' and pad_x1 > 0:
        canvas.move(player_pad, -PLAYER_PAD_SPEED * width_factor, 0)

def increase_y_velocity(y_velocity: int, amount: int):
    '''
    It returns Y_VELOCITY increased by AMOUNT if there is\n
    availablity of increasing without going off MAXIMUM_Y_VELOCITY
    '''
    if 0 < y_velocity <= MAXIMUM_Y_VELOCITY - amount :
        return y_velocity + amount
    
    elif -MAXIMUM_Y_VELOCITY + amount <= y_velocity < 0:
        return y_velocity - amount
    
    else: 
        return y_velocity

def destroy_collided_block(y_velocity: int) -> int:
    '''
    It destroys any collided block(s) and returns new y_velocity
    '''
    global gameover, score
    
    # Store any canvas items appeared above the ball in a list
    collisions_with_ball = list(canvas.find_overlapping(*canvas.coords(ball)))

    # If there's other than the ball in those coords
    # AND player_pad isn't with them
    if len(collisions_with_ball) > 1 and player_pad not in collisions_with_ball:
        Thread(target=lambda: play_sfx('block_destroyed')).start()

        # Remove the ball to get only the collided block
        collisions_with_ball.remove(ball)
        collided_block = collisions_with_ball[0]
        blocks_data['blocks list'].remove(collided_block)
        canvas.delete(collided_block)

        score += 1
        score_label.config(text=str(score))
        
        if score % 10 == 0 and score != 0: # Because 0 % 10 is also 0
            Thread(target=lambda: play_sfx('ten_blocks_destroyed')).start()

        if check('win', not blocks_data['blocks list']): # It might be the last block
            gameover = True

        # Randomly, return velocity as it is
        # so the ball continues breaking other blocks.
        return -y_velocity if randint(1, 10) > 4 else y_velocity
    else:
        return y_velocity # Continue your way; As there is no collision with any block

def spawn_ball(y_velocity):
    '''
    It creates the BALL and return X_VELOCITY and Y_VELOCITY
    in a way that the BALL go up right
    '''
    global ball
    ball = canvas.create_oval(10,
                              canvas_dimensions['height']-10,
                              40,
                              canvas_dimensions['height']-40,
                              fill='red')
    return (10, -abs(y_velocity)) # x and y velocity

def ball_movement_logic(x_velocity = 10, y_velocity = -10):
    '''
    It holds the ball movement logic, and mostly about inflections.
    '''
    global gameover, lives

    if gameover:
        return
    else:
        ball_coords = canvas.coords(ball)
        x1, y1, x2, y2 = [round(v) for v in ball_coords]

        if x2 > canvas_dimensions['width'] or x1 < 0: # If the ball reaches an edge on the right/left
            x_velocity = -x_velocity

        if y1 < 0: # If the ball reaches the top edge
            y_velocity = abs(y_velocity)
            y_velocity = increase_y_velocity(y_velocity, 3)
        
        if y2 > canvas_dimensions['height']: # If the ball reaches the bottom edge (not striked by the player's pad)
            lives -= 1
            lives_label.config(text=f'{str(lives)} :المحاولات')

            if check('lose', lives < 1):
                gameover = True
                return
            else:
                canvas.delete(ball)
                x_velocity, y_velocity = spawn_ball(y_velocity)

        # If the player's pad got overlapped by the ball (striked the ball)
        if y_velocity > 0 and ball in canvas.find_overlapping(*canvas.coords(player_pad)):
            y_velocity = -abs(y_velocity)

        canvas.move(ball, x_velocity, y_velocity)
        y_velocity = destroy_collided_block(y_velocity)

        # So the ball movement logic continue until GAMEOVER
        canvas.after(DELAY, lambda: ball_movement_logic(x_velocity, y_velocity))

def generate_blocks():
    '''
    It creates blocks according to blocks_data, BLOCK_WIDTH and BLOCK_HEIGHT
    '''
    block_y = 10
    for row in range(blocks_data['rows number']):
        block_x = 10
        for i in range(blocks_data['blocks number']):
            color = '#' + ''.join(choices(HEXADECIMALS, k=6))
            blocks_data['blocks list'].append(canvas.create_rectangle(block_x,
                                                block_y,
                                                block_x + BLOCK_WIDTH,
                                                block_y + BLOCK_HEIGHT,
                                                fill=color))
            block_x += BLOCK_WIDTH + GAP

        block_y += BLOCK_HEIGHT + GAP

def open_game_window():
    '''
    It opens the game_window and creates its components to start playing
    '''
    global game_window, player_pad, player_pad_width, ball, score_label, lives_label, canvas, gameover, score, lives

    Thread(target=lambda: play_sfx('menu_btn_clicked')).start()

    score = 0
    lives = 3
    gameover = False

    game_window = Toplevel(window, width=canvas_dimensions['width'], height=canvas_dimensions['height'])
    game_window.resizable(False, False)
    '''
    اكتب ملاحظات وارفع على قيت هب واسجل مقطع ختامي
    +
    عدد المستطيلات حسب العرض
    '''
    canvas = Canvas(game_window, width=canvas_dimensions['width'], height=canvas_dimensions['height'], bg='black')
    canvas.pack()
    
    player_pad_width = player_pad_width/2 * width_factor
    player_pad = canvas.create_rectangle(canvas_dimensions['width']/2 - player_pad_width,
                                         canvas_dimensions['height']-30,
                                         canvas_dimensions['width']/2 + player_pad_width,
                                         canvas_dimensions['height']-10,
                                         fill='white')

    ball = canvas.create_oval(10,
                              canvas_dimensions['height']-10,
                              40,
                              canvas_dimensions['height']-40,
                              fill='red')
    
    score_label = Label(game_window, text=str(score), bg='black', fg='lightblue', font=('', 16, 'bold'))
    lives_label = Label(game_window, text=f'{str(lives)} :المحاولات', bg='black', fg='lightblue', font=('', 16, 'bold'))

    score_label.pack(expand=True, fill='both')
    lives_label.pack(expand=True, fill='both')

    generate_blocks()
    ball_movement_logic()

    game_window.focus()
    game_window.bind('<Key>', move_player_pad)
    game_window.bind('<Destroy>', lambda _: playBtn.config(state='normal'))

    playBtn.config(state='disabled')

def putMaxSettings(*args):
    ...

def check_values_validaty(*args: int):
    '''
    the ARGS should be ordered that way:
        0. width
        1. canvas_dimensions['height']
        2. blocksNumber 
        3. rowsNumber
    '''
    horizontalSpaceNeeded = GAP + (BLOCK_WIDTH + GAP) * args[2] 
    verticalSpaceNeeded = GAP + (BLOCK_HEIGHT + GAP) * args[3] 

    if horizontalSpaceNeeded >= args[0] + 20 or verticalSpaceNeeded >= args[1] // 2:
        showerror('خطأ', 'عرض/طول لوحة اللعب لا تكفي\nجرب تغيير بعض القيم، كالطول والعرض، أو عدد المستطيلات والصفوف')
        return False

    validValuesRanges = [1200 >= args[0] >= 600, 600 >= args[1] >= 400]
    valuesAreValid = all(validValuesRanges)

    if valuesAreValid:
        return True
    else:
        showerror('خطأ', 'يجب إدخال قيم متناسبة مع النطاق المذكور')
        return False

def save_settings(*args):
    global settings_window, width_factor, adaptPadToWidthVar

    try:
        args = [int(arg) for arg in args]
    except ValueError:
        showerror('خطأ', 'يجب إدخال القيم على صورة أعداد صحيحة فقط')
    else:
        if check_values_validaty(*args):
            width_factor = args[0] / canvas_dimensions['width'] if adaptPadToWidthVar.get() else 1
            canvas_dimensions['width'], canvas_dimensions['height'], blocks_data['blocks number'], blocks_data['rows number'] = args
            settings_window.destroy()
            Thread(target=lambda: play_sfx('settings_saved')).start()

            # print(adaptPadToWidthVar.get())

def open_settings():
    global blocksNumber, rowsNumber, settings_window, adaptPadToWidthVar

    Thread(target=lambda: play_sfx('menu_btn_clicked')).start()

    settings_window = Toplevel(window)
    settings_window.title('الإعدادات')
    settings_window.config(bg='black')
    settings_window.minsize(250, 400)
    settings_window.maxsize(250, 400)

    settingsList = {('عرض لوحة اللعب (النطاق 600-1200)', canvas_dimensions['width']): Entry(settings_window, justify='center'),
                    ('طول لوحة اللعب (النطاق 400-800)', canvas_dimensions['height']): Entry(settings_window, justify='center'),
                    ('عدد المربعات لكل صف', blocks_data['blocks number']): Entry(settings_window, justify='center'),
                    ('عدد الصفوف', blocks_data['rows number']): Entry(settings_window, justify='center')}
    
    adaptPadToWidthBtn = Checkbutton(settings_window, text='يتأقلم المِضرَب مع حجم لوحة اللعب',
                                     bg='black', fg='lightblue',
                                     variable=adaptPadToWidthVar,
                                     onvalue=1, offvalue=0,
                                     selectcolor="#464646")
    adaptPadToWidthBtn.pack(expand=True, fill='x', ipady=10)

    for item in settingsList.items():
        Label(settings_window, text=item[0][0], bg='black', fg='lightblue').pack(padx=20, pady=5)
        item[1].pack(padx=20, pady=5)
        item[1].insert(0, str(item[0][1]))

    largestSettingsBtn = Button(settings_window, BTN_STYLING_STYLE, text='تحديد الإعدادات القصوى',
                                command=lambda: putMaxSettings(*[e.get() for e in settingsList.values()]))

    saveBtn = Button(settings_window, BTN_STYLING_STYLE, text='حفظ', 
                     command=lambda: save_settings(*[e.get() for e in settingsList.values()]))
    
    largestSettingsBtn.pack(BTN_PACK, pady=(10, 0), ipady=10)
    saveBtn.pack(BTN_PACK, ipady=10)

    settingsBtn.config(state='disabled')
    settings_window.bind('<Destroy>', lambda _: settingsBtn.config(state='normal'))
    

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

playBtn = Button(window, BTN_STYLING_STYLE, text='العب', font=('', 16, 'bold'), command=open_game_window)

settingsBtn = Button(window, BTN_STYLING_STYLE, text='إعدادات اللعبة',
                    font=('', 16, 'bold'), command=open_settings)

adaptPadToWidthVar = BooleanVar(value=True)

if hasTitleImage:
    titleImageLabel.pack(expand=True, fill='x')
else:
    titleImageLabel.pack(ipadx=100, ipady=50)

playBtn.pack(BTN_PACK)
settingsBtn.pack(BTN_PACK)

window.mainloop()