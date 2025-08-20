from pynput import mouse, keyboard
import pyautogui
from time import sleep

def on_press(key):
    try:
        # Check if Alt+0 is pressed
        if key == keyboard.KeyCode.from_char('0'):
            x, y = pyautogui.position()
            pyautogui.moveTo(x + 3, y)  # Move mouse 50px right
    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    # Keep track of released keys
    if key in pressed_keys:
        pressed_keys.remove(key)

def on_press_wrapper(key):
    pressed_keys.add(key)
    on_press(key)

pressed_keys = set()

with keyboard.Listener(on_press=on_press_wrapper, on_release=on_release) as listener:
    listener.join()

# while True:
#     x, y = pyautogui.position()
#     print((x, y))
#     pyautogui.moveTo(x + 3, y)
#     sleep(0.5)