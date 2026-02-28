"""
pressingKeys GUI - Automated directional key press simulator.

Reads directional instructions (left, right, up, down) from clipboard text,
optionally inverts them, and simulates the corresponding key presses in the
focused application with natural human-like delays.

Author: MANGOBA
Version: 28-Feb-2026
"""

from __future__ import annotations

import os
import re
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

try:
    import keyboard
    import pyperclip
except ImportError as details:
    print("-E- Couldn't import module, try pip install 'module'")
    raise details

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INVERT_MAP: dict[str, str] = {
    "left": "right",
    "right": "left",
    "up": "down",
    "down": "up",
}

DEFAULT_START_HOTKEY = "F6"
DEFAULT_ABORT_HOTKEY = "F7"

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def key_press(key: str) -> None:
    """Simulate a natural key press with random delays."""
    time.sleep(random.uniform(0.07, 0.09))
    keyboard.press(key)
    time.sleep(random.uniform(0.05, 0.07))
    keyboard.release(key)


def parse_keys(text: str, invert: bool) -> list[str]:
    """Parse directional keys from *text*, optionally inverting them."""
    text = text.replace("\n", "").replace(".", "")
    text = re.sub(r"[0-9]", "", text)
    keys = re.findall(r"left|right|up|down", text, re.IGNORECASE)
    if invert:
        return [INVERT_MAP.get(k.lower(), k.lower()) for k in keys]
    return [k.lower() for k in keys]


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------


class PressingKeysApp:
    """Tkinter GUI for pressingKeys."""

    def __init__(self) -> None:
        # --- state ---
        self.invert = True
        self.running = False
        self.aborted = False
        self.worker_thread: threading.Thread | None = None

        # --- hotkey state ---
        self.start_hotkey: str = DEFAULT_START_HOTKEY
        self.abort_hotkey: str = DEFAULT_ABORT_HOTKEY
        self._listening_for: str | None = None  # "start" or "abort" while assigning
        self._kb_hook_id: int | None = None

        # --- clipboard monitoring state ---
        self._last_clipboard: str = ""

        # --- root window ---
        self.root = tk.Tk()
        self.root.title("pressingKeys")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # Try to use the ico file if available
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self._build_ui()

    # ---- UI construction --------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # --- Mode toggle ---
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(fill="x", **pad)

        self.toggle_btn = tk.Button(
            mode_frame, text="INVERTED", width=14, font=("Segoe UI", 10, "bold"),
            bg="#d35400", fg="white", command=self._toggle_mode,
        )
        self.toggle_btn.pack(side="left")

        # --- Key list input ---
        input_frame = tk.LabelFrame(self.root, text="Key list")
        input_frame.pack(fill="both", expand=True, **pad)

        self.text_input = scrolledtext.ScrolledText(
            input_frame, width=40, height=10, font=("Consolas", 9),
        )
        self.text_input.pack(fill="both", expand=True, padx=4, pady=4)

        # --- Paste button ---
        paste_frame = tk.Frame(self.root)
        paste_frame.pack(fill="x", **pad)

        self.paste_btn = tk.Button(
            paste_frame, text="Paste from clipboard", width=20,
            command=self._paste_clipboard,
        )
        self.paste_btn.pack(side="left")

        self.key_count_var = tk.StringVar(value="Keys: 0")
        tk.Label(paste_frame, textvariable=self.key_count_var,
                 font=("Segoe UI", 9)).pack(side="right")

        # --- Control buttons ---
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(fill="x", **pad)

        self.start_btn = tk.Button(
            ctrl_frame, text="Start", width=12, bg="#27ae60", fg="white",
            font=("Segoe UI", 10, "bold"), command=self._start,
        )
        self.start_btn.pack(side="left", padx=(0, 4))

        self.abort_btn = tk.Button(
            ctrl_frame, text="Abort", width=12, bg="#c0392b", fg="white",
            font=("Segoe UI", 10, "bold"), command=self._abort, state="disabled",
        )
        self.abort_btn.pack(side="left")

        # --- Hotkey assignment ---
        hotkey_frame = tk.LabelFrame(self.root, text="Hotkeys (global)")
        hotkey_frame.pack(fill="x", **pad)

        # Start hotkey row
        start_hk_row = tk.Frame(hotkey_frame)
        start_hk_row.pack(fill="x", padx=4, pady=2)
        tk.Label(start_hk_row, text="Start:", width=6, anchor="w",
                 font=("Segoe UI", 9)).pack(side="left")
        self.start_hk_var = tk.StringVar(value=self.start_hotkey)
        tk.Label(start_hk_row, textvariable=self.start_hk_var, width=14,
                 font=("Consolas", 9, "bold"), relief="groove", anchor="center",
                 ).pack(side="left", padx=(0, 4))
        self.assign_start_btn = tk.Button(
            start_hk_row, text="Assign", width=8,
            command=lambda: self._begin_hotkey_assign("start"),
        )
        self.assign_start_btn.pack(side="left")

        # Abort hotkey row
        abort_hk_row = tk.Frame(hotkey_frame)
        abort_hk_row.pack(fill="x", padx=4, pady=2)
        tk.Label(abort_hk_row, text="Abort:", width=6, anchor="w",
                 font=("Segoe UI", 9)).pack(side="left")
        self.abort_hk_var = tk.StringVar(value=self.abort_hotkey)
        tk.Label(abort_hk_row, textvariable=self.abort_hk_var, width=14,
                 font=("Consolas", 9, "bold"), relief="groove", anchor="center",
                 ).pack(side="left", padx=(0, 4))
        self.assign_abort_btn = tk.Button(
            abort_hk_row, text="Assign", width=8,
            command=lambda: self._begin_hotkey_assign("abort"),
        )
        self.assign_abort_btn.pack(side="left")

        # --- Status bar ---
        self.status_var = tk.StringVar(value="Ready — paste or type a key list to begin.")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var, anchor="w",
            font=("Segoe UI", 9), relief="sunken", bd=1,
        )
        status_bar.pack(fill="x", side="bottom", ipady=2)

        # --- Log area ---
        log_frame = tk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, **pad)

        self.log_output = scrolledtext.ScrolledText(
            log_frame, width=40, height=6, font=("Consolas", 9), state="disabled",
        )
        self.log_output.pack(fill="both", expand=True, padx=4, pady=4)

        # Register global hotkeys
        self._register_global_hotkeys()

        # Start clipboard monitoring
        self._poll_clipboard()

    # ---- Hotkey assignment ------------------------------------------------

    def _register_global_hotkeys(self) -> None:
        """Register global hotkeys for start and abort via the keyboard lib."""
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        keyboard.add_hotkey(self.start_hotkey, self._global_start, suppress=False)
        keyboard.add_hotkey(self.abort_hotkey, self._global_abort, suppress=False)

    def _global_start(self) -> None:
        """Called from the global keyboard hook — schedule on main thread."""
        self.root.after(0, self._start)

    def _global_abort(self) -> None:
        """Called from the global keyboard hook — schedule on main thread."""
        self.root.after(0, self._abort)

    def _begin_hotkey_assign(self, which: str) -> None:
        """Put the UI in 'listening' mode for the next key press."""
        if self.running or self._listening_for is not None:
            return
        self._listening_for = which
        if which == "start":
            self.assign_start_btn.config(text="Press key…", state="disabled")
            self.assign_abort_btn.config(state="disabled")
        else:
            self.assign_abort_btn.config(text="Press key…", state="disabled")
            self.assign_start_btn.config(state="disabled")
        self.status_var.set(f"Press any key to assign as {which.upper()} hotkey…")
        self._log(f"Listening for {which} hotkey…")

        # Use a keyboard hook to capture the very next key (works globally)
        self._kb_hook_id = keyboard.on_press(self._on_hotkey_captured, suppress=False)

    def _on_hotkey_captured(self, event: keyboard.KeyboardEvent) -> None:
        """Callback from keyboard hook when a key is pressed during assign."""
        key_name: str = event.name  # e.g. 'f6', 'a', 'ctrl'
        # Unhook immediately
        if self._kb_hook_id is not None:
            keyboard.unhook(self._kb_hook_id)
            self._kb_hook_id = None
        # Schedule the rest on the main thread
        self.root.after(0, self._finish_hotkey_assign, key_name)

    def _finish_hotkey_assign(self, key_name: str) -> None:
        which = self._listening_for
        self._listening_for = None

        if which == "start":
            self.start_hotkey = key_name
            self.start_hk_var.set(key_name)
            self.assign_start_btn.config(text="Assign", state="normal")
            self.assign_abort_btn.config(state="normal")
        elif which == "abort":
            self.abort_hotkey = key_name
            self.abort_hk_var.set(key_name)
            self.assign_abort_btn.config(text="Assign", state="normal")
            self.assign_start_btn.config(state="normal")

        self._register_global_hotkeys()
        self._log(f"{which.capitalize()} hotkey set to: {key_name}")
        self.status_var.set("Ready — paste or type a key list to begin.")

    # ---- Actions ----------------------------------------------------------

    def _toggle_mode(self) -> None:
        if self.running:
            return
        self.invert = not self.invert
        if self.invert:
            self.toggle_btn.config(text="INVERTED", bg="#d35400")
        else:
            self.toggle_btn.config(text="NORMAL", bg="#2980b9")
        self._log(f"Mode: {'INVERTED' if self.invert else 'NORMAL'}")
        self._update_key_count()

    def _paste_clipboard(self) -> None:
        try:
            clip = pyperclip.paste()
        except Exception:
            self._log("Failed to read clipboard.")
            return
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", clip)
        self._update_key_count()
        self._log("Pasted key list from clipboard.")

    def _update_key_count(self) -> None:
        text = self.text_input.get("1.0", "end")
        keys = parse_keys(text, self.invert)
        self.key_count_var.set(f"Keys: {len(keys)}")

    def _start(self) -> None:
        if self.running:
            return
        text = self.text_input.get("1.0", "end")
        keys = parse_keys(text, self.invert)
        if not keys:
            self._log("No keys to press. Paste a key list first.")
            return

        self.running = True
        self.aborted = False
        self._set_controls_running(True)
        self._log(f"Starting — {len(keys)} keys, mode={'INVERTED' if self.invert else 'NORMAL'}.")
        self.status_var.set(f"Running… focus the target app! Press {self.abort_hotkey} to abort.")

        self.worker_thread = threading.Thread(
            target=self._run_keys, args=(keys,), daemon=True,
        )
        self.worker_thread.start()

    def _run_keys(self, keys: list[str]) -> None:
        t0 = time.time()
        pressed = 0
        for key in keys:
            if self.aborted:
                break
            key_press(key)
            pressed += 1
            # Also check the physical abort hotkey while target app has focus
            if keyboard.is_pressed(self.abort_hotkey):
                self.aborted = True
                break
        t1 = time.time()

        elapsed = int(t1 - t0)
        if self.aborted:
            msg = f"Aborted after {pressed}/{len(keys)} keys ({elapsed}s)."
        else:
            msg = f"Finished — {pressed} keys in {elapsed}s."

        # Schedule UI updates on the main thread
        self.root.after(0, self._finish, msg)

    def _finish(self, msg: str) -> None:
        self.running = False
        self._set_controls_running(False)
        self._log(msg)
        self.status_var.set("Done. Ready for next run.")

    def _abort(self) -> None:
        if self.running:
            self.aborted = True

    def _set_controls_running(self, running: bool) -> None:
        state_normal = "disabled" if running else "normal"
        state_abort = "normal" if running else "disabled"
        self.start_btn.config(state=state_normal)
        self.toggle_btn.config(state=state_normal)
        self.paste_btn.config(state=state_normal)
        self.text_input.config(state=state_normal)
        self.abort_btn.config(state=state_abort)
        self.assign_start_btn.config(state=state_normal)
        self.assign_abort_btn.config(state=state_normal)

    # ---- Helpers ----------------------------------------------------------

    def _poll_clipboard(self) -> None:
        """Check the clipboard every 500ms and auto-populate if it contains keys."""
        if not self.running and self._listening_for is None:
            try:
                clip = pyperclip.paste()
            except Exception:
                clip = ""
            if clip and clip != self._last_clipboard:
                self._last_clipboard = clip
                # Only auto-populate if the clipboard contains directional keys
                keys = parse_keys(clip, invert=False)
                if keys:
                    self.text_input.delete("1.0", "end")
                    self.text_input.insert("1.0", clip)
                    self._update_key_count()
                    self._log(f"Clipboard detected — {len(keys)} keys loaded.")
        self.root.after(500, self._poll_clipboard)

    def _log(self, msg: str) -> None:
        self.log_output.config(state="normal")
        self.log_output.insert("end", msg + "\n")
        self.log_output.see("end")
        self.log_output.config(state="disabled")

    def run(self) -> None:
        """Start the Tk main loop."""
        self.root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    PressingKeysApp().run()
