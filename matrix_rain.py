"""
Matrix digital rain — runs in your terminal.
Usage: python matrix_rain.py
Press Ctrl+C to exit.
"""

import os
import random
import time
import sys

CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

GREEN  = "\033[32m"
BRIGHT = "\033[1;32m"
DIM    = "\033[2;32m"
RESET  = "\033[0m"
HIDE   = "\033[?25l"
SHOW   = "\033[?25h"
CLEAR  = "\033[2J\033[H"


def get_size():
    size = os.get_terminal_size()
    return size.columns, size.lines


def move(row, col):
    sys.stdout.write(f"\033[{row};{col}H")


class Drop:
    def __init__(self, col, height):
        self.col = col
        self.head = random.randint(-height, 0)
        self.length = random.randint(6, 24)
        self.speed = random.uniform(0.5, 1.5)
        self.timer = 0.0

    def step(self, dt):
        self.timer += dt
        if self.timer >= 1.0 / self.speed:
            self.timer = 0.0
            self.head += 1
            return True
        return False

    def render(self, width, height):
        for i in range(self.length):
            row = self.head - i
            if row < 1 or row > height:
                continue
            move(row, self.col)
            if i == 0:
                sys.stdout.write(BRIGHT + random.choice(CHARS))
            elif i < 3:
                sys.stdout.write(GREEN + random.choice(CHARS))
            else:
                sys.stdout.write(DIM + random.choice(CHARS))

        tail = self.head - self.length
        if 1 <= tail <= height:
            move(tail, self.col)
            sys.stdout.write(RESET + " ")

    def is_done(self, height):
        return self.head - self.length > height


def main():
    sys.stdout.write(HIDE + CLEAR)
    sys.stdout.flush()

    width, height = get_size()
    drops = [Drop(col, height) for col in range(1, width + 1, 2)]
    last = time.time()

    try:
        while True:
            now = time.time()
            dt = now - last
            last = now

            w, h = get_size()
            if w != width or h != height:
                width, height = w, h
                sys.stdout.write(CLEAR)
                drops = [Drop(col, height) for col in range(1, width + 1, 2)]

            for d in drops:
                if d.step(dt):
                    d.render(width, height)
                if d.is_done(height):
                    d.__init__(d.col, height)

            # random glitch flicker
            if random.random() < 0.1:
                r = random.randint(1, height)
                c = random.randint(1, width)
                move(r, c)
                sys.stdout.write(BRIGHT + random.choice(CHARS))

            sys.stdout.flush()
            time.sleep(0.03)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + SHOW + CLEAR)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
