# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A single-file Python terminal animation (`matrix_rain.py`) that renders the Matrix
digital rain effect using ANSI escape codes and Python's standard library only.
No dependencies. See `SPEC.md` for full architecture detail.

## Running the program

```bash
python3 matrix_rain.py                              # defaults
python3 matrix_rain.py --color blue --speed 2.0    # with options
python3 matrix_rain.py --help                       # all flags
```

Keyboard controls while running: `+`/`-` speed · `c` cycle color · `r` reset · `q` quit

## Architecture in one paragraph

`Config` (dataclass) holds mutable runtime state (speed, color, density). `Drop`
(dataclass) represents one falling column — owns its position, trail length, and
pace. `run()` sets the terminal to raw mode via `tty.setraw()`, then loops at ~33
fps: reads a non-blocking keypress with `select()`, advances each `Drop` by
delta-time, and redraws only changed rows using ANSI cursor-movement codes. On exit,
`termios.tcsetattr()` restores the original terminal state.

## Key implementation details

- **Raw terminal mode** — `tty.setraw()` + `termios` are required for live keypresses;
  always restore with `termios.tcsetattr()` in a `finally` block or the shell breaks.
- **Delta-time stepping** — each `Drop` accumulates `dt` against `1.0 / (pace × speed)`
  so animation speed is frame-rate-independent.
- **ANSI only** — no `curses`. Every draw operation is a raw `\033[...` escape written
  to `sys.stdout`.
- **No dependencies** — keep it that way; the zero-install property is a core goal.

## Files

| File | Purpose |
|------|---------|
| `matrix_rain.py` | Entire program — single file |
| `SPEC.md` | Architecture reference, component docs, design decisions |
| `README.md` | User-facing docs: usage, options, controls, how it works |
