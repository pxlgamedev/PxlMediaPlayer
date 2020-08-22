###############################################
# A User Interface module for BearLibTerminal #
#     Provided free to use by PxLGameDev      #
###############################################

'''
This module distills some basic UI design concepts into easy to use functions
which can be called from anywhere in your regular program.

There are two primary design concepts in the following functions:

The 'Draw' functions, such as draw_rect and draw_panel, are little more than
basic shapes to be displayed on screen at the given w and h value, with a size
determined by width and height.

The 'Interactive' functions, such as text_button, will also handle mouse coords
and return true if the mouse is in position over the button. These functions
are called with a simple if statement, it's up to the calling script to handle
mouse clicks.

EXAMPLE:

if UI.button_text(4, 3, 'Mute') and key == 128:
    self.mute = not self.mute

'''

from bearlibterminal import terminal


def draw_panel(w, h, width, height, color):
    bg = '[color=' + color + ']'
    for i in range(width):
        bg = bg + '▓'
    for i in range(height):
       terminal.printf(w, h + i, bg)

def draw_rect(w, h, width, height):
    top = '┌'
    mid = '│'
    bottom = '└'
    for i in range(width - 2):
        top = top + '─'
        mid = mid + ' '
        bottom = bottom + '─'
    top = top + '┐'
    mid = mid + '│'
    bottom = bottom + '┘'
    terminal.printf(w, h, top)
    for i in range(height - 2):
        terminal.printf(w, h + 1 + i, mid)
    terminal.printf(w, h + height - 1, bottom)
    pass

'''
Window is a group of funcitons, drawing a panel, a rect, and an 'X' button
'''
def draw_window(w, h, width, height, color, x, offset='[offset=-10x-10]'):
    draw_panel(w, h, width, height, color)
    draw_rect(w, h, width, height)
    close = 'X'
    mouse_over = False
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if (w + width == mouse[0] + 2 or w + width == mouse[0] + 1) and (h == mouse[1] or h == mouse[1] -1):
        close = '[color=' + x + ']X'
        mouse_over = True
    terminal.printf(w + width - 2, h, '┬')
    terminal.printf(w + width - 2, h + 1, '└┤')
    terminal.printf(w + width - 1, h + 1, offset + close)
    return mouse_over

'''
This is a simple button that changes color while the mouse is over the text.
'''
def button_text(w, h, text, color, offset='', bg=''):
    mouse_over = False
    width = terminal.measure(text)[0]
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if h == mouse[1] and (mouse[0] <= w + width and mouse[0] >= w):
        text = '[color=' + color + ']' + text
        mouse_over = True
    else:
        text = bg + text
    terminal.printf(w, h, text)
    return mouse_over

def button_sliding(w, h, text, color, key=False):
    mouse_over = False
    width = terminal.measure(text)[0]
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if key or (h == mouse[1] or h == mouse[1] -1) and (mouse[0] <= w + width and mouse[0] >= w):
        text = text
        mouse_over = True
    else:
        text = '[color=' + color + ']' + text
    terminal.printf(w, h, text)
    return mouse_over

'''
These Slider functions take an input float value as 'p' for position.
They will then create a string to display that float value within the
range of either width, or height, depending on which slider is used.

The string is printed at the given coords, and a new p value is
calculated from the mouse position over those coords. This allows
a value such as volume to be displayed and interacted with directly.

As it returns two values it requires a more verbose 'if statement':

bar, pos = UI.slider_v(1, 15, 10, volume)
if bar and key == 128:
    volume = pos
'''

def slider_h(w, h, width, p, color):
    bg = '[color=' + color + ']'
    mouse_over = False
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    new = int(width * p)
    for i in range(new):
        bg = bg + '▓'
    if (h == mouse[1] or h == mouse[1] -1) and (mouse[0] <= w + width and mouse[0] >= w):
        mouse_over = True
        p = (mouse[0] - w) / width
    terminal.printf(w, h, bg)
    return mouse_over, p

def slider_v(w, h, height, p, color):
    color = '[color=' + color + ']'
    bg = ''
    mouse_over = False
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    new = int(height * p)
    for i in range(new):
        bg = bg + '▓'
    if (w == mouse[0] or w == mouse[0] -1) and (mouse[1] <= h and mouse[1] >= h - height):
        mouse_over = True
        p = -(mouse[1] - h) / height
    for i in range(len(bg)):
        terminal.printf(w, h - i, color + bg[i])
    return mouse_over, p

'''
color_selector recieves an RGB color value as a string ie: '255,255,255'

The color is split and the values converted to floats for the sliders.
The slider values are then converted back to string and returned.

swatch, new_color = UI.color_selector(w, h, 40, color)
if swatch and key == 128:
    color = new_color
'''

def color_selector(w, h, width, color):
    mouse_over = False
    rgb = color.split(',')
    r = int(rgb[0]) / 255
    g = int(rgb[1]) / 255
    b = int(rgb[2]) / 255
    draw_rect(w, h, width + 2, 3)
    tr, r = slider_h(w+1, h+1, width, r, color)
    draw_rect(w, h+2, width + 2, 3)
    tg, g = slider_h(w+1, h+3, width, g, color)
    draw_rect(w, h+4, width + 2, 3)
    tb, b = slider_h(w+1, h+5, width, b, color)
    if tr or tg or tb:
        mouse_over = True
    new_color = str(int(r * 255)) + ',' + str(int(g * 255)) + ',' + str(int(b * 255))
    return mouse_over, new_color
