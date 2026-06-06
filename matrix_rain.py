"""
Matrix digital rain — terminal animation using ANSI escape codes.
Usage:  python3 matrix_rain.py [--speed N] [--color COLOR] [--density N]
Controls (while running):  +/-  speed   c  cycle color   r  reset   q  quit
"""

import argparse
import os
import random
import sys
import termios
import time
import tty
from dataclasses import dataclass, field
from select import select

__version__ = "0.2.0"

CHARS = (
    "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ"
    "ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

THEMES = {
    "green": ("\033[32m",   "\033[1;32m", "\033[2;32m"),
    "blue":  ("\033[34m",   "\033[1;34m", "\033[2;34m"),
    "red":   ("\033[31m",   "\033[1;31m", "\033[2;31m"),
    "white": ("\033[37m",   "\033[1;37m", "\033[2;37m"),
}
THEME_ORDER = list(THEMES.keys())

RESET = "\033[0m"
HIDE  = "\033[?25l"
SHOW  = "\033[?25h"
CLEAR = "\033[2J\033[H"


@dataclass
class Config:
    speed:   float = 1.0
    color:   str   = "green"
    density: float = 0.5


@dataclass
class Drop:
    col:    int
    head:   int   = field(init=False)
    length: int   = field(init=False)
    pace:   float = field(init=False)
    timer:  float = 0.0

    def __post_init__(self):
        self.reset(height=40)

    def reset(self, height: int):
        self.head   = random.randint(-height, 0)
        self.length = random.randint(6, 24)
        self.pace   = random.uniform(0.5, 1.5)
        self.timer  = 0.0

    def step(self, dt: float, speed: float) -> bool:
        self.timer += dt
        if self.timer >= 1.0 / (self.pace * speed):
            self.timer = 0.0
            self.head += 1
            return True
        return False

    def render(self, width: int, height: int, theme: tuple):
        normal, bright, dim = theme
        for i in range(self.length):
            row = self.head - i
            if row < 1 or row > height:
                continue
            _move(row, self.col)
            if i == 0:
                sys.stdout.write(bright + random.choice(CHARS))
            elif i < 3:
                sys.stdout.write(normal + random.choice(CHARS))
            else:
                sys.stdout.write(dim + random.choice(CHARS))

        tail = self.head - self.length
        if 1 <= tail <= height:
            _move(tail, self.col)
            sys.stdout.write(RESET + " ")

    def is_done(self, height: int) -> bool:
        return self.head - self.length > height


def _move(row: int, col: int):
    sys.stdout.write(f"\033[{row};{col}H")


def _get_size() -> tuple[int, int]:
    s = os.get_terminal_size()
    return s.columns, s.lines


def _read_key() -> str | None:
    """Return a single keypress if one is waiting, else None (non-blocking)."""
    if select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def _make_drops(width: int, height: int, density: float) -> list[Drop]:
    cols = [c for c in range(1, width + 1, 2) if random.random() < density]
    if not cols:
        cols = list(range(1, width + 1, 2))
    return [Drop(col) for col in cols]


def run(cfg: Config):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    sys.stdout.write(HIDE + CLEAR)
    sys.stdout.flush()

    try:
        tty.setraw(fd)
        width, height = _get_size()
        drops = _make_drops(width, height, cfg.density)
        theme_idx = THEME_ORDER.index(cfg.color)
        last = time.time()

        while True:
            now = time.time()
            dt  = now - last
            last = now

            # handle keyboard
            key = _read_key()
            if key in ("q", "\x03"):  # q or Ctrl+C (raw mode intercepts SIGINT)
                break
            elif key == "+":
                cfg.speed = min(cfg.speed + 0.2, 5.0)
            elif key == "-":
                cfg.speed = max(cfg.speed - 0.2, 0.1)
            elif key == "c":
                theme_idx = (theme_idx + 1) % len(THEME_ORDER)
                cfg.color = THEME_ORDER[theme_idx]
            elif key == "r":
                sys.stdout.write(CLEAR)
                drops = _make_drops(width, height, cfg.density)

            # resize
            w, h = _get_size()
            if w != width or h != height:
                width, height = w, h
                sys.stdout.write(CLEAR)
                drops = _make_drops(width, height, cfg.density)

            theme = THEMES[cfg.color]
            for d in drops:
                if d.step(dt, cfg.speed):
                    d.render(width, height, theme)
                if d.is_done(height):
                    d.reset(height)

            # random glitch flicker
            if random.random() < 0.08:
                _move(random.randint(1, height), random.randint(1, width))
                sys.stdout.write(theme[1] + random.choice(CHARS))

            sys.stdout.flush()
            time.sleep(0.03)

    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.stdout.write(RESET + SHOW + CLEAR)
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Matrix digital rain terminal animation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Controls while running:  + / -  speed    c  color    r  reset    q  quit",
    )
    parser.add_argument("--speed",   type=float, default=1.0,     metavar="N",
                        help="animation speed multiplier (0.1–5.0, default 1.0)")
    parser.add_argument("--color",   choices=THEME_ORDER, default="green",
                        help="color theme (default: green)")
    parser.add_argument("--density", type=float, default=0.5,     metavar="N",
                        help="fraction of columns active (0.1–1.0, default 0.5)")
    parser.add_argument("--version", action="version", version=f"matrix_rain {__version__}")
    args = parser.parse_args()

    cfg = Config(
        speed   = max(0.1, min(5.0, args.speed)),
        color   = args.color,
        density = max(0.1, min(1.0, args.density)),
    )
    run(cfg)


if __name__ == "__main__":
    main()
