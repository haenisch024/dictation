"""
Listens for a ctrl+space hotkey.
hotkey_pressed() returns true if the hotkey pair is pressed.
Hotkey is suppressed for the rest of the system.
Works for both Windows and OSX (darwin).
"""
from pynput import keyboard


pressed_keys = set()

def on_press(key):
    pressed_keys.add(key)

def on_release(key):
    try:
        pressed_keys.remove(key)
    except KeyError:
        pass

def ctrl_pressed():
    # return keyboard.Key.ctrl in pressed_keys
    ctrl_keys = {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
    return any(k in pressed_keys for k in ctrl_keys)

def hotkey_pressed():
    # Check that any of the control keys and the space key are pressed
    return (keyboard.Key.space in pressed_keys) and ctrl_pressed()

def darwin_intercept(event_type, event):
    # This executes *after* on_press and on_release so hotkey_pressed()
    # will be true already when we decide if we should suppress the final key of the hotkey
    if hotkey_pressed():
        print('darwin suppress hotkey')
        return None
    else:
        return event
    
def win32_event_filter(msg, data):
    # This executes *before* on_press and on_release so we must
    # check if the first key of the hotkey is pressed to determine
    # if we should suppress the last key of the hot key.
    # We also have to check if the last key is being pressed or released.
    # Since we will suppress the last key, we will add it to the pressed
    # keys here rather than in on_press
    # vkCode for <space> is 0x20
    # msg is 256 for key down and 257 for key up
    if ctrl_pressed() and data.vkCode == 0x20 and msg == 256:
        pressed_keys.add(keyboard.Key.space)
        keyboardListener.suppress_event()
    
# Start the listener in a separate thread
keyboardListener = keyboard.Listener(on_press=on_press,
                             on_release=on_release,
                             darwin_intercept=darwin_intercept,
                             win32_event_filter=win32_event_filter)
def hotkey_start():
    keyboardListener.start()

def hotkey_stop():
    keyboardListener.stop()