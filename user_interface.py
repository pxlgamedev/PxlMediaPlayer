from bearlibterminal import terminal

from configparser import ConfigParser

config = ConfigParser()
config.read('main.ini')

def select_color(string):
    c = config.get('default', string)
    return c

def draw_window(w, h, width, height, offset='[offset=-10x-10]'):
    draw_panel(w, h, width, height)
    draw_rect(w, h, width, height)
    close = 'X'
    mouse_over = False
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if (w + width == mouse[0] + 2 or w + width == mouse[0] + 1) and (h == mouse[1] or h == mouse[1] -1):
        close = '[color=' + select_color('close') + ']X'
        mouse_over = True
    terminal.printf(w + width - 2, h, '┬')
    terminal.printf(w + width - 2, h + 1, '└┤')
    terminal.printf(w + width - 1, h + 1, offset + close)
    return mouse_over

def draw_panel(w, h, width, height):
    bg = '[color=' + select_color('hud') + ']'
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

def button_text(w, h, text, offset='', color=''):
    mouse_over = False
    width = terminal.measure(text)[0]
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if h == mouse[1] and (mouse[0] <= w + width and mouse[0] >= w):
        text = '[color=' + select_color('selected') + ']' + text
        mouse_over = True
    else:
        text = color + text
    terminal.printf(w, h, text)
    return mouse_over

def button_sliding(w, h, text, key=False):
    mouse_over = False
    width = terminal.measure(text)[0]
    mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if key or (h == mouse[1] or h == mouse[1] -1) and (mouse[0] <= w + width and mouse[0] >= w):
        text = text
        mouse_over = True
    else:
        text = '[color=grey] ' + text
    terminal.printf(w, h, text)
    return mouse_over

def time_bar(w, h, width, p):
    bg = '[color=' + select_color('timebar') + ']'
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
