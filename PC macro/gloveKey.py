from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import time

mouse = MouseController()
keyboard = KeyboardController()

# === T9 and Number Maps ===
T9_MAP = {
    'Key2': 'abc',
    'Key3': 'def',
    'Key4': 'ghi',
    'Key5': 'jkl',
    'Key6': 'mno',
    'Key7': 'pqrs',
    'Key8': 'tuv',
    'Key9': 'wxyz',
    'Key1': '.,!?'
}

NUMBER_MAP = {
    'Key1': '1',
    'Key2': '2',
    'Key3': '3',
    'Key4': '4',
    'Key5': '5',
    'Key6': '6',
    'Key7': '7',
    'Key8': '8',
    'Key9': '9',
    'Key0': '0'
}

# === T9 State ===
class T9State:
    def __init__(self):
        self.last_key = None
        self.press_count = 0
        self.last_press_time = 0
        self.upper = False
        self.number_mode = False
        self.delay = 0.5  # 0.5s flush timeout

    def toggle_case(self):
        self.upper = not self.upper
        print(f"🔁 Case Toggled: {'UPPER' if self.upper else 'lower'}")

    def toggle_number_mode(self):
        self.number_mode = not self.number_mode
        print(f"🔁 Number Mode: {'ON' if self.number_mode else 'OFF'}")

    def update_key(self, key):
        now = time.time()
        if key == self.last_key and (now - self.last_press_time) < self.delay:
            self.press_count += 1
        else:
            self.flush()
            self.last_key = key
            self.press_count = 0
        self.last_press_time = now

    def flush(self):
        if self.last_key and self.last_key in T9_MAP:
            chars = T9_MAP[self.last_key]
            char = chars[self.press_count % len(chars)]
            if self.upper:
                char = char.upper()
            print(f"🔤 Typed: {char}")
            keyboard.type(char)
        self.last_key = None
        self.press_count = 0

t9 = T9State()

# === Special Functional Keys ===
def send_special(keyname):
    if keyname == 'Key0':
        keyboard.type(' ')
    elif keyname == 'KeyD':
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    elif keyname == 'KeyA':
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
    elif keyname == 'Key*':
        t9.toggle_case()
    elif keyname == 'KeyB':
        t9.toggle_number_mode()

# === Macro Movement Mapping ===
macro_map = {
    (10, -10): 'Key1',
    (-20, 20): 'Key2',
    (15, -30): 'Key3',
    (-25, -25): 'Key4',
    (30, -15): 'Key5',
    (-15, 30): 'Key6',
    (40, -40): 'Key7',
    (-35, 10): 'Key8',
    (25, -5): 'Key9',
    (-50, 50): 'Key0',
    (60, -60): 'KeyA',
    (-70, 70): 'KeyB',
    (80, -10): 'KeyC',
    (-90, 90): 'KeyD',
    (100, -100): 'Key*',
    (-110, 110): 'Key#'
}

# === Listener Setup ===
last_x, last_y = mouse.position
last_trigger_time = time.time()
cooldown = 0.2  # faster detection

print("🎯 T9 Macro Listener Started — Press Ctrl+C to exit.")

try:
    while True:
        x, y = mouse.position
        dx = x - last_x
        dy = y - last_y

        if abs(dx) > 5 or abs(dy) > 5:
            now = time.time()
            if now - last_trigger_time > cooldown:
                coords = (dx, dy)
                if coords in macro_map:
                    keyname = macro_map[coords]
                    print(f"✅ Key Triggered: {keyname}")

                    if t9.number_mode and keyname in NUMBER_MAP:
                        t9.flush()
                        print(f"🔢 Typed: {NUMBER_MAP[keyname]}")
                        keyboard.type(NUMBER_MAP[keyname])
                    elif keyname in T9_MAP:
                        t9.update_key(keyname)
                    else:
                        t9.flush()
                        send_special(keyname)

                    last_trigger_time = now

        # Flush if idle timeout reached
        if t9.last_key and time.time() - t9.last_press_time > t9.delay:
            t9.flush()

        last_x, last_y = x, y
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n👋 Listener stopped.")
