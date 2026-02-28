# pressingKeys

A GUI-based directional key press simulator that reads arrow-key instructions from your clipboard and replays them into the focused application with natural human-like timing. Supports **inverted** mode (left ↔ right, up ↔ down) toggled with a single button.

> **Looking for the CLI version?** It lives on the [`legacy`](https://github.com/mangobax/pressingKeys/tree/legacy) branch.

---

## Features

- **Tkinter GUI** — no terminal required; always-on-top window with key list editor, log panel, and status bar.
- **Direction inversion toggle** — click the mode button to switch between **INVERTED** and **NORMAL**. Defaults to inverted.
- **Automatic clipboard detection** — copy a key list anywhere and it's loaded into the app automatically.
- **Customisable global hotkeys** — assign any key as the Start or Abort hotkey via the UI. Hotkeys work even while the target app has focus.
- **Human-like timing** — randomised delays between key presses to avoid ghosting.
- **Abort support** — stop a run mid-sequence with the Abort button or hotkey.

---

## Demo

![pressingKeys demo](example.gif)

---

## Getting Started

### Option A — Download the executable

Download the latest [pressingKeys.exe](https://github.com/mangobax/pressingKeys/releases/latest) release.

### Option B — Run from source

```bash
git clone https://github.com/mangobax/pressingKeys.git
cd pressingKeys
pip install -r requirements.txt
python pressingKeys.py
```

Or [download the ZIP](https://github.com/mangobax/pressingKeys/archive/main.zip) and extract it.

### Dependencies

- [keyboard](https://pypi.org/project/keyboard/)
- [pyperclip](https://pypi.org/project/pyperclip/)

> All other imports (`os`, `time`, `random`, `re`, `threading`, `tkinter`) are part of the Python standard library.

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

3. **Load keys** — either:
   - **Copy** a key list to the clipboard — the app detects it automatically and populates the key list box.
   - Click **Paste from clipboard** to manually load the current clipboard.
   - Type or edit keys directly in the text area.

4. **Choose mode** — click the mode button at the top to toggle between **INVERTED** (orange) and **NORMAL** (blue).

5. **Configure hotkeys (optional)** — in the *Hotkeys (global)* section, click **Assign** next to Start or Abort, then press any key to bind it. Defaults: `F6` (Start), `F7` (Abort).

6. **Focus the target app** — click on the application where the keys should be pressed.

7. **Start** — click the **Start** button or press your Start hotkey. The key presses will be sent automatically.

8. **Abort (optional)** — click **Abort** or press your Abort hotkey to stop early.

### Default Hotkeys

| Action | Default Key |
|--------|-------------|
| Start  | `F6`        |
| Abort  | `F7`        |

> Hotkeys are global and work even when the target application has focus. Reassign them at any time via the **Assign** buttons.

### Performance

With default timing settings, **100 keys ≈ 10 ± 5 seconds**.

---

## Legacy CLI Version

The original terminal-based version (with `Ctrl` to start, `Shift` to restart, `Esc` to quit) is preserved on the [`legacy`](https://github.com/mangobax/pressingKeys/tree/legacy) branch.

---

## Known Limitations

- Reducing the random delay intervals may cause missed keystrokes.
- Only arrow-key directions (`left`, `right`, `up`, `down`) are supported.
- The `keyboard` library requires elevated privileges on Linux.

---

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) license. See [LICENSE](LICENSE) for details.

You are free to share and adapt this work for non-commercial purposes, as long as you give appropriate credit and distribute any derivative work under the same license.