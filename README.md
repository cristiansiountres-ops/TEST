# Matrix Rain

A terminal animation that renders the **Matrix digital rain** effect — columns of
falling half-width katakana and alphanumeric characters — using only Python's standard
library and ANSI escape codes. No packages to install.

![green rain falling in a terminal](https://raw.githubusercontent.com/cristiansiountres-ops/TEST/main/docs/preview.txt)

---

## What it does

Simulates the iconic green cascade from *The Matrix* directly in your terminal.
Each column on screen gets an independent "drop" — a stream of random characters
that falls at its own speed. The head of each drop glows bright white-green; the
tail fades to dim green before disappearing.

Everything is drawn using **ANSI escape codes**: sequences of characters that tell
the terminal where to move the cursor and what color to print. No graphics library
needed — just text.

---

## Requirements

- Python 3.10 or newer
- A terminal that supports ANSI color codes (macOS Terminal, iTerm2, Windows Terminal, any Linux terminal)

---

## Quick start

```bash
git clone https://github.com/cristiansiountres-ops/TEST.git
cd TEST
python3 matrix_rain.py
```

---

## Options

```
python3 matrix_rain.py [--speed N] [--color COLOR] [--density N]

  --speed N      Animation speed multiplier, 0.1–5.0  (default: 1.0)
  --color COLOR  Color theme: green | blue | red | white  (default: green)
  --density N    Fraction of columns active, 0.1–1.0  (default: 0.5)
  --version      Show version and exit
```

**Examples**

```bash
# Fast blue rain at full density
python3 matrix_rain.py --color blue --speed 2.5 --density 1.0

# Slow, sparse red rain
python3 matrix_rain.py --color red --speed 0.3 --density 0.2
```

---

## Keyboard controls (while running)

| Key | Action |
|-----|--------|
| `+` | Speed up |
| `-` | Slow down |
| `c` | Cycle color theme |
| `r` | Reset / clear screen |
| `q` or Ctrl+C | Quit |

---

## How it works (the short version)

1. **Drop objects** — one per active column. Each tracks its head position, tail
   length, and its own speed multiplier (so drops fall at different rates).
2. **Render loop** — runs ~33 times per second. Each tick advances drops by a
   delta-time amount and redraws only the characters that changed (head moves
   down one row, tail erases one row). Full-screen redraws are avoided.
3. **ANSI escape codes** — `\033[row;colH` moves the cursor; `\033[32m` sets green;
   `\033[1;32m` sets bright green. The terminal does the actual rendering.
4. **Non-blocking keyboard** — `tty.setraw()` puts the terminal in raw mode so
   keypresses arrive immediately (no Enter needed). `select()` checks for input
   without blocking the render loop.

For full architecture detail see [SPEC.md](SPEC.md).

---

## Things to try next (ideas for you)

- Add a `--message` flag that "rains" the letters of a word you choose
- Make the drop length configurable (`--min-length`, `--max-length`)
- Add a "reveal" mode that slowly shows a hidden image made of characters
- Port it to another language (JavaScript in Node.js, Go, Rust)

---

## License

MIT — do whatever you want with it.
