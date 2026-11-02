#!/usr/bin/env python3
"""
nullmatrix - a cmatrix clone where keys 1-0 switch what the rain is made of.

Keys:
  1-9, 0   switch mode
  + / -    faster / slower
  p        pause
  q        quit

Run:  python3 nullmatrix.py        (Windows: pip install windows-curses)
"""
import curses
import locale
import random

MODES = {
    "1": ("classic",  "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789", curses.COLOR_GREEN),
    "2": ("binary",   "01", curses.COLOR_CYAN),
    "3": ("hex",      "0123456789ABCDEF", curses.COLOR_YELLOW),
    "4": ("symbols",  "!@#$%^&*()_+-=[]{};:,.<>/?|~`\\", curses.COLOR_RED),
    "5": ("letters",  "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", curses.COLOR_MAGENTA),
    "6": ("braille",  "".join(chr(c) for c in range(0x2801, 0x2900)), curses.COLOR_CYAN),
    "7": ("blocks",   "░▒▓█▀▄▌▐▖▗▘▝▚▞┃━╋╬║═", curses.COLOR_BLUE),
    "8": ("cyrillic", "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯабвгдежзийклмнопрстуфхцчшщэюя", curses.COLOR_WHITE),
    "9": ("runes",    "".join(chr(c) for c in range(0x16A0, 0x16EB)), curses.COLOR_RED),
    "0": ("null",     "∅Ø0øⵁ∄⊘⌀○◌", None),
}

FPS = 30


class Column:
    def __init__(self, height, stagger=True):
        self.reset(height, stagger)

    def reset(self, height, stagger=False):
        self.length = random.randint(max(4, height // 4), max(6, height))
        self.speed = random.uniform(0.25, 1.0)
        self.y = -random.uniform(0, height * 2 if stagger else height)


def main(stdscr):
    locale.setlocale(locale.LC_ALL, "")
    curses.curs_set(0)
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK

    for i in range(8):
        curses.init_pair(i + 1, i, bg)
    HEAD = curses.color_pair(8)

    stdscr.nodelay(False)
    stdscr.timeout(int(1000 / FPS))

    mode = "1"
    speed_mul = 1.0
    paused = False
    label_frames = FPS * 2
    rainbow = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_GREEN,
               curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA]

    def setup():
        h, w = stdscr.getmaxyx()
        cols = [Column(h) for _ in range(w)]
        grid = [[" "] * w for _ in range(h)]
        return h, w, cols, grid

    h, w, cols, grid = setup()

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            break
        elif key == curses.KEY_RESIZE:
            curses.update_lines_cols()
            h, w, cols, grid = setup()
            continue
        elif 0 <= key < 256 and chr(key) in MODES:
            mode = chr(key)
            label_frames = FPS * 2
            for row in grid:
                for x in range(len(row)):
                    row[x] = " "
        elif key in (ord("+"), ord("=")):
            speed_mul = min(4.0, speed_mul + 0.2)
        elif key in (ord("-"), ord("_")):
            speed_mul = max(0.2, speed_mul - 0.2)
        elif key in (ord("p"), ord("P")):
            paused = not paused

        name, chars, color = MODES[mode]
        stdscr.erase()

        for x, col in enumerate(cols):
            if not paused:
                old_head = int(col.y)
                col.y += col.speed * speed_mul
                new_head = int(col.y)
                for r in range(old_head + 1, new_head + 1):
                    if 0 <= r < h:
                        grid[r][x] = random.choice(chars)
                if col.y - col.length > h:
                    col.reset(h)

            head = int(col.y)
            c = color if color is not None else rainbow[x % len(rainbow)]
            pair = curses.color_pair(c + 1)

            for age in range(col.length + 1):
                r = head - age
                if r < 0 or r >= h:
                    continue
                ch = grid[r][x]
                if ch == " ":
                    continue
                if not paused and age > 0 and random.random() < 0.02:
                    ch = grid[r][x] = random.choice(chars)

                if age == 0:
                    attr = HEAD | curses.A_BOLD
                elif age < 3:
                    attr = pair | curses.A_BOLD
                elif age < col.length * 0.6:
                    attr = pair
                else:
                    attr = pair | curses.A_DIM
                try:
                    stdscr.addstr(r, x, ch, attr)
                except curses.error:
                    pass

        if label_frames > 0:
            label_frames -= 1
            text = f" nullmatrix [{mode}] {name} "
            try:
                stdscr.addstr(0, 0, text[: w - 1], curses.A_REVERSE)
            except curses.error:
                pass

        stdscr.refresh()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
