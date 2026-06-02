# SPEC — Matrix Rain

Version `0.2.0` · single file: `matrix_rain.py`

---

## Problem being solved

Classic terminal screensavers (like `cmatrix`) require a C compiler and the `ncurses`
library. This project achieves the same visual effect in **pure Python** using only
the standard library, making it easy to read, modify, and learn from.

---

## Goals

| Goal | Decision |
|------|----------|
| Zero dependencies | Use `os`, `sys`, `tty`, `termios`, `select`, `random`, `time`, `argparse` only |
| Real-time, interactive | Raw terminal mode + non-blocking input via `select()` |
| Configurable at launch | `argparse` CLI flags |
| Configurable while running | Single-key controls in the render loop |
| Readable code | One class (`Drop`), one config object (`Config`), one run loop |

---

## Architecture

```
main()
  └─ parse args → Config
  └─ run(cfg)
       ├─ tty.setraw()          put terminal in raw mode
       ├─ _make_drops()         create one Drop per active column
       └─ render loop (33 fps)
            ├─ _read_key()      non-blocking keypress check
            ├─ resize check     recreate drops if terminal resized
            ├─ Drop.step()      advance each drop's position
            ├─ Drop.render()    draw changed rows via ANSI codes
            └─ Drop.is_done()   reset drops that fall off screen
```

---

## Key components

### `Config` (dataclass)

Holds mutable runtime state shared across the loop:

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `speed` | float | 1.0 | Multiplier applied to all drop speeds |
| `color` | str | "green" | Active theme name (key into `THEMES`) |
| `density` | float | 0.5 | Probability each column gets a drop |

### `Drop` (dataclass)

One instance per active terminal column. Owns its own position and pace so each
column animates independently.

| Field | Meaning |
|-------|---------|
| `col` | Terminal column (1-indexed) |
| `head` | Current row of the leading character |
| `length` | How many rows the trail spans |
| `pace` | Per-drop speed multiplier (randomised 0.5–1.5) |
| `timer` | Accumulates delta-time between steps |

**`step(dt, speed)`** — accumulates `dt` and returns `True` once enough time has
passed to advance the head by one row. The threshold is `1.0 / (pace × speed)`.

**`render(width, height, theme)`** — writes only the characters that belong to this
drop's current position. Three brightness levels:
- Row 0 (head): `bright` — glowing white-green
- Rows 1–2: `normal` — solid green
- Rows 3+: `dim` — faded green

**`is_done(height)`** — true when the tail has scrolled completely off the bottom.
The drop resets with a new random length and pace rather than being destroyed.

### Render loop

Runs at ~33 fps (`time.sleep(0.03)`). Uses **delta-time** (`dt = now - last`) so
the animation speed is consistent regardless of how long each frame takes to draw.

### ANSI escape codes used

| Code | Effect |
|------|--------|
| `\033[row;colH` | Move cursor to row, col |
| `\033[32m` | Normal green |
| `\033[1;32m` | Bright green |
| `\033[2;32m` | Dim green |
| `\033[0m` | Reset all attributes |
| `\033[?25l` / `\033[?25h` | Hide / show cursor |
| `\033[2J\033[H` | Clear screen and home cursor |

### Non-blocking keyboard input

`tty.setraw()` switches the terminal from **canonical mode** (line-buffered, waits
for Enter) to **raw mode** (every keypress delivered immediately). `select()` with a
timeout of `0` checks whether a byte is waiting without blocking. On exit,
`termios.tcsetattr()` restores the original terminal settings so the shell continues
to work normally.

---

## File layout

```
TEST/
├── matrix_rain.py   main program (single file)
├── README.md        user-facing documentation
└── SPEC.md          this file — architecture and design notes
```

---

## Future ideas

- `--message TEXT` — rain the characters of a word/phrase
- `--fps N` — configurable frame rate
- Multicolor mode — each drop picks its own color
- Save/restore terminal state more robustly on crash (signal handler)
