import time
import machine
from machine import I2C, Pin, PWM
from ssd1306 import SSD1306_I2C
from hid_services import Mouse

# === INITIAL SETUP ===
orientation_mode = 0
az_offset = 0.0
ay_offset = 0.0
keypad_mode = False

# Pins
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 32, i2c)

RED = Pin(19, Pin.OUT)
GREEN = Pin(18, Pin.OUT)
BLUE = Pin(5, Pin.OUT)

CLK = Pin(39, Pin.IN, Pin.PULL_UP)
DT = Pin(34, Pin.IN, Pin.PULL_UP)
ROT_SW = Pin(35, Pin.IN, Pin.PULL_UP)

rows = [Pin(pin, Pin.OUT) for pin in (32, 33, 25, 26)]
cols = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in (27, 14, 12, 13)]

main_button = Pin(17, Pin.IN, Pin.PULL_UP)
left_click_button = Pin(4, Pin.IN, Pin.PULL_UP)
right_click_button = Pin(16, Pin.IN, Pin.PULL_UP)

buzzer_pin = Pin(2, Pin.OUT)
buzzer_pin.value(0)
buzzer = PWM(buzzer_pin)
buzzer.freq(2000)
buzzer.duty(0)

vibrator = PWM(Pin(15))
vibrator.freq(2000)
vibrator.duty(0)

mouse = Mouse("ESP32 Glove Mouse")

speeds = [3.0, 4.0, 5.5]
current_speed_index = 0

last_dt_state = DT.value()
last_rotary_press_time = time.ticks_ms()
rotary_click_last = ROT_SW.value()
rotary_click_last_time = time.ticks_ms()
last_main_button_state = main_button.value()
last_key_time = time.ticks_ms()

keypad_map = [['D', 'C', 'B', 'A'],
              ['#', '9', '6', '3'],
              ['0', '8', '5', '2'],
              ['*', '7', '4', '1']]

macro_coords = {
    '1': (10, -10),
    '2': (-20, 20),
    '3': (15, -30),
    '4': (-25, -25),
    '5': (30, -15),
    '6': (-15, 30),
    '7': (40, -40),
    '8': (-35, 10),
    '9': (25, -5),
    '0': (-50, 50),
    'A': (60, -60),
    'B': (-70, 70),
    'C': (80, -10),
    'D': (-90, 90),
    '*': (100, -100),
    '#': (-110, 110),
}

def scan_keypad_macro_mode():
    global last_key_time
    now = time.ticks_ms()
    if time.ticks_diff(now, last_key_time) < 300:
        return
    for row_num, row_pin in enumerate(rows):
        row_pin.value(0)
        for col_num, col_pin in enumerate(cols):
            if col_pin.value() == 0:
                key = keypad_map[row_num][col_num]
                if key in macro_coords:
                    x, y = macro_coords[key]
                    print(f"[MACRO] {key} → Move to ({x}, {y})")
                    mouse.set_axes(x=x, y=y)
                    mouse.notify_hid_report()
                    vibrate(0.1)
                    last_key_time = now
                    while col_pin.value() == 0:
                        time.sleep(0.01)
        row_pin.value(1)

def set_rgb(r, g, b):
    RED.value(not r)
    GREEN.value(not g)
    BLUE.value(not b)

def vibrate(duration=0.2, intensity=512):
    vibrator.duty(intensity)
    time.sleep(duration)
    vibrator.duty(0)

def play_tone(duration_ms=100, frequency=2000):
    buzzer.freq(frequency)
    buzzer.duty(512)
    time.sleep_ms(duration_ms)
    buzzer.duty(0)

def play_connected_chime():
    play_tone(120, 880)   # A5
    play_tone(120, 988)   # B5
    play_tone(120, 1047)  # C6
    play_tone(150, 1319)  # E6

def play_mode_switch_chime():
    play_tone(100, 988)   # B5
    play_tone(120, 784)   # G5

def update_speed_indicator():
    if current_speed_index == 0:
        set_rgb(0, 1, 0)  # Green
    elif current_speed_index == 1:
        set_rgb(0, 0, 1)  # Blue
    elif current_speed_index == 2:
        set_rgb(1, 0, 0)  # Red

def check_rotary_button():
    global current_speed_index, last_dt_state, last_rotary_press_time
    dt_state = DT.value()
    now = time.ticks_ms()
    if dt_state != last_dt_state:
        if time.ticks_diff(now, last_rotary_press_time) > 300:
            current_speed_index = (current_speed_index + 1) % len(speeds)
            update_speed_indicator()
            vibrate(0.1)
            last_rotary_press_time = now
    last_dt_state = dt_state

def check_rotary_click():
    global orientation_mode, rotary_click_last_time, rotary_click_last, az_offset, ay_offset
    current_click = ROT_SW.value()
    now = time.ticks_ms()
    if current_click == 0 and rotary_click_last == 1:
        if time.ticks_diff(now, rotary_click_last_time) > 300:
            orientation_mode ^= 1
            rotary_click_last_time = now
            _, ay, az = read_accel()
            az_offset = az if orientation_mode == 1 else 0.0
            ay_offset = ay if orientation_mode == 1 else 0.0
            oled.fill(0)
            oled.text("Orientation:", 0, 0)
            oled.text("Vertical" if orientation_mode else "Horizontal", 0, 12)
            oled.show()
            vibrate(0.2)
    rotary_click_last = current_click

def init_mpu6050():
    i2c.writeto_mem(0x68, 0x6B, b'\x00')
    time.sleep(0.1)

def read_accel():
    def convert(data):
        val = int.from_bytes(data, 'big')
        return val - 65536 if val > 32767 else val
    ax = convert(i2c.readfrom_mem(0x68, 0x3B, 2)) / 16384.0
    ay = convert(i2c.readfrom_mem(0x68, 0x3D, 2)) / 16384.0
    az = convert(i2c.readfrom_mem(0x68, 0x3F, 2)) / 16384.0
    return ax, ay, az

def ble_mouse_start():
    mouse.start()
    mouse.start_advertising()
    oled.fill(0)
    oled.text("ESP32 Mouse", 10, 0)
    oled.text("Pairing...", 20, 15)
    oled.show()
    while not mouse.is_connected():
        time.sleep(0.1)
    if mouse.is_advertising():
        mouse.stop_advertising()
    play_connected_chime()    
    time.sleep(2)
    oled.fill(0)
    oled.text("Mode:", 0, 0)
    oled.text("Keypad" if keypad_mode else "Mouse", 0, 12)
    oled.show()

# === STARTUP SEQUENCE ===
set_rgb(1, 1, 1)
init_mpu6050()
update_speed_indicator()
oled.fill(0)
oled.text("Press Main BTN", 0, 0)
oled.text("to start BLE", 0, 10)
oled.show()

# === MAIN LOOP ===
while True:
    if main_button.value() == 0:
        while main_button.value() == 0:
            time.sleep(0.01)
        ble_mouse_start()

        while mouse.is_connected():
            if main_button.value() == 0 and last_main_button_state == 1:
                keypad_mode = not keypad_mode
                oled.fill(0)
                oled.text("Mode Switched:", 0, 0)
                oled.text("Keypad" if keypad_mode else "Mouse", 0, 12)
                oled.show()
                vibrate(0.2)
                play_mode_switch_chime()
            last_main_button_state = main_button.value()

            if keypad_mode:
                scan_keypad_macro_mode()
            else:
                check_rotary_button()
                check_rotary_click()
                ax, ay, az = read_accel()
                if abs(ax) < 0.4: ax = 0
                if abs(ay) < 0.4: ay = 0
                if abs(az) < 0.4: az = 0
                speed = speeds[current_speed_index]
                if orientation_mode == 0:
                    move_x = int(ax * 10 * speed)
                    move_y = int(ay * 10 * speed)
                else:
                    adjusted_az = az - az_offset
                    adjusted_ay = ay - ay_offset
                    if abs(adjusted_az) < 0.3: adjusted_az = 0
                    if abs(adjusted_ay) < 0.3: adjusted_ay = 0
                    move_x = int(adjusted_az * 10 * speed)
                    move_y = int(adjusted_ay * 10 * speed)
                #move_x = max(-10, min(10, move_x))
                #move_y = max(-10, min(10, move_y))
                if move_x != 0 or move_y != 0:
                    mouse.set_axes(x=move_x, y=move_y)
                    mouse.notify_hid_report()

                if left_click_button.value() == 0:
                    mouse.set_buttons(1, 0, 0)
                    mouse.notify_hid_report()
                    time.sleep(0.1)
                    mouse.set_buttons(0, 0, 0)
                    mouse.notify_hid_report()

                if right_click_button.value() == 0:
                    mouse.set_buttons(0, 1, 0)
                    mouse.notify_hid_report()
                    time.sleep(0.1)
                    mouse.set_buttons(0, 0, 0)
                    mouse.notify_hid_report()

            time.sleep(0.05)
    time.sleep(0.05)