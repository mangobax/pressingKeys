# pressingKeys

An automated directional key press simulator that reads arrow-key instructions from your clipboard and replays them into the focused application with natural human-like timing. Supports an **inverted** mode (left ↔ right, up ↔ down) that can be toggled on or off before each run.

---

## Features

- **Direction inversion toggle** — press `I` to switch between **INVERTED** (left ↔ right, up ↔ down) and **NORMAL** mode before each run. Defaults to inverted.
- **Human-like timing** — randomised delays between key presses to avoid ghosting.
- **Abort support** — press `Q` at any time to stop mid-sequence.
- **Always-on-top terminal** — the console stays visible while another app has focus (Windows).
- **Clipboard-driven** — no file dialogs; just copy your key list and go.

---

## Getting Started

### Option A — Download the executable

Download the latest [pressingKeys.exe](https://github.com/marcoagbarreto/pressingKeys/releases/download/v0.2.4/pressingKeys.exe) release.

### Option B — Run from source

```bash
git clone https://github.com/marcoagbarreto/pressingKeys.git
cd pressingKeys
pip install -r requirements.txt
python pressingKeys.py
```

Or [download the ZIP](https://github.com/marcoagbarreto/pressingKeys/archive/main.zip) and extract it.

### Dependencies

- [keyboard](https://pypi.org/project/keyboard/)
- [pyperclip](https://pypi.org/project/pyperclip/)

> All other imports (`os`, `time`, `random`, `re`) are part of the Python standard library.

---

## Usage

1. **Prepare a key list** — create a text file with directional instructions. See [`keyList.txt`](keyList.txt) for an example:

   ```text
   1.upupup
   4.upleftleft
   7.downleftdown
   10.rightdowndown
   13.rightupup
   ```

   Numbers and periods are stripped automatically — only the keywords `left`, `right`, `up`, and `down` are extracted (case-insensitive).

2. **Launch the program** — run `pressingKeys.exe` or `python pressingKeys.py`.

3. **Choose mode** — the current mode (`INVERTED` or `NORMAL`) is shown on screen. Press `I` to toggle before copying your key list.

4. **Copy the key list** — select your text and press `Ctrl+C`. The program detects the clipboard update and parses the keys.

5. **Focus the target app** — click on the application where the keys should be pressed.

6. **Start** — press `Ctrl` to begin. The key presses will be sent automatically (inverted or not, depending on the active mode).

7. **Abort (optional)** — press `Q` at any time to stop early.

8. **Restart or quit** — after a run, press `Shift` to go again or `Esc` to exit.

### Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Toggle invert/normal mode | `I` |
| Copy key list to clipboard | `Ctrl+C` |
| Start pressing keys | `Ctrl` |
| Abort current run | `Q` |
| Restart | `Shift` |
| Quit | `Esc` |

### Performance

With default timing settings, **100 keys ≈ 10 ± 5 seconds**.

---

## Known Limitations

- Reducing the random delay intervals may cause missed keystrokes.
- Only arrow-key directions (`left`, `right`, `up`, `down`) are supported.
- The always-on-top terminal feature is Windows-only.

---

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) license. See [LICENSE](LICENSE) for details.

You are free to share and adapt this work for non-commercial purposes, as long as you give appropriate credit and distribute any derivative work under the same license.