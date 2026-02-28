"""
pressingKeys - Automated directional key press simulator.

Reads directional instructions (left, right, up, down) from clipboard text,
inverts them, and simulates the corresponding key presses in the focused
application with natural human-like delays.

Author: MANGOBA
Version: 28-Feb-2026
"""

try:
    import os
    import time
    import random
    import re
    import keyboard
    import pyperclip
except ImportError as details:
    print("-E- Couldn't import module, try pip install 'module'")
    raise details

INVERT_MAP: dict[str, str] = {
    'left': 'right',
    'right': 'left',
    'up': 'down',
    'down': 'up',
}


def key_press(key: str) -> None:
    """Simulate a natural key press with random delays."""
    # sleeps to avoid key ghosting from previous key press
    time.sleep(random.uniform(0.07, 0.09))
    keyboard.press(key)
    # sleeps between 0.05 and 0.07 seconds to simulate natural pressing
    time.sleep(random.uniform(0.05, 0.07))
    keyboard.release(key)


class PressingKeys:
    def __init__(self, text: str, invert: bool = True) -> None:
        self.key_list: list[str] = self._parse_keys(text, invert)

    @staticmethod
    def _parse_keys(text: str, invert: bool) -> list[str]:
        """Parse directional keys from text, optionally inverting them."""
        text = text.replace('\n', '').replace('.', '')
        text = re.sub(r'[0-9]', '', text)
        keys = re.findall(r'left|right|up|down', text, re.IGNORECASE)
        if invert:
            return [INVERT_MAP.get(k.lower(), k.lower()) for k in keys]
        return [k.lower() for k in keys]

    def run(self) -> None:
        """Wait for start key, then press all keys in sequence."""
        print('Ensure to have focus on the app.')
        print(f'Keys to press: {len(self.key_list)}')

        start_key = 'Ctrl'
        abort_key = 'Q'
        print(f'Press [{start_key}] to start.')
        keyboard.wait(start_key)
        print(f'Started, press [{abort_key}] to abort.')

        t0 = time.time()
        for key in self.key_list:
            key_press(key)
            if keyboard.is_pressed(abort_key):
                print('Aborted')
                break

        t1 = time.time()
        print('Finished')
        print(f'Time elapsed: {int(t1 - t0)}s')


def clear_terminal() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def setup_windows_terminal() -> None:
    """Resize terminal and set it to always-on-top (Windows only)."""
    if os.name != 'nt':
        return

    os.system('mode con cols=37 lines=12')
    os.system(
        'Powershell.exe -ExecutionPolicy UnRestricted -Command "(Add-Type -memberDefinition'
        ' \\"[DllImport(\\"\\"user32.dll\\"\\")] public static extern bool SetWindowPos'
        '(IntPtr hWnd, IntPtr hWndInsertAfter, int x,int y,int cx, int xy, uint flagsw);\\"'
        ' -name \\"Win32SetWindowPos\\" -passThru )::SetWindowPos((Add-Type -memberDefinition'
        ' \\"[DllImport(\\"\\"Kernel32.dll\\"\\")] public static extern IntPtr'
        ' GetConsoleWindow();\\" -name \\"Win32GetConsoleWindow\\" -passThru'
        ' )::GetConsoleWindow(),-1,0,0,0,0,67)"'
    )


def main() -> None:
    copy_key = 'Ctrl+C'
    restart_key = 'Shift'
    quit_key = 'Esc'
    toggle_key = 'I'
    invert = True

    setup_windows_terminal()
    clear_terminal()

    while True:
        mode = 'INVERTED' if invert else 'NORMAL'
        print(f'Mode: {mode}  (press [{toggle_key}] to toggle)')
        print(f'Waiting for items in the clipboard,\nuse [{copy_key}] to copy the key list.')
        print(f'Press [{quit_key}] to quit.')

        # Wait for either clipboard copy or toggle key
        while True:
            if keyboard.is_pressed(toggle_key):
                invert = not invert
                mode = 'INVERTED' if invert else 'NORMAL'
                print(f'Mode switched to: {mode}')
                time.sleep(0.3)  # debounce
            if keyboard.is_pressed(copy_key):
                break
            if keyboard.is_pressed(quit_key):
                print('Goodbye!')
                return
            time.sleep(0.05)

        time.sleep(0.1)  # Sleep 0.1 s so clipboard can refresh

        PressingKeys(pyperclip.paste(), invert=invert).run()

        print(f'Press [{restart_key}] to start again, or [{quit_key}] to quit.')
        while True:
            if keyboard.is_pressed(restart_key):
                break
            if keyboard.is_pressed(quit_key):
                print('Goodbye!')
                return
            time.sleep(0.05)
        clear_terminal()


if __name__ == '__main__':
    main()
