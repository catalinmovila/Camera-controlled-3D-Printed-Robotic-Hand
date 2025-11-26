"""
Keyboard controller for robotic hand (Pinkie → Thumb).

Keys (case-insensitive):
  1-5  = Open individual fingers  (clockwise  → CW)
  Q-T  = Close individual fingers (counter-clockwise → CCW)
  O    = Open  ALL fingers
  C    = Close ALL fingers
  Esc  = Quit
"""

import serial
import time
import sys

# ───────── Serial (ESP32 / Arduino) ─────────
ESP_PORT = "COM4"        # ← set Windows port here (e.g. COM4, COM5, …)
BAUD     = 115_200

try:
    esp = serial.Serial(ESP_PORT, BAUD, timeout=1)
    time.sleep(2)        # allow board to reboot
    print(f"[INFO] Serial open on {ESP_PORT} @ {BAUD} baud")
except serial.SerialException as e:
    sys.exit(f"[ERROR] Could not open {ESP_PORT}: {e}")

# ───────── Keyboard hook (cross-platform) ─────────
try:
    import keyboard      # pip install keyboard
except ImportError:
    sys.exit("[ERROR] Install the 'keyboard' package:  pip install keyboard")

# ───────── Key-to-command mapping ─────────
# Format: 'key' : (serial_byte,   human-readable action,      finger_name)
key_to_command = {
    # ── OPEN (clockwise) ─────────────────────────────────────────
    '1': ('1', 'open (CW)',  'Pinkie'),   # 1  → open pinkie
    '2': ('2', 'open (CW)',  'Ring'),     # 2  → open ring
    '3': ('3', 'open (CW)',  'Middle'),   # 3  → open middle
    '4': ('4', 'open (CW)',  'Index'),    # 4  → open index
    '5': ('5', 'open (CW)',  'Thumb'),    # 5  → open thumb

    # ── CLOSE (counter-clockwise) ────────────────────────────────
    'q': ('q', 'close (CCW)', 'Pinkie'),  # Q  → close pinkie
    'w': ('w', 'close (CCW)', 'Ring'),    # W  → close ring
    'e': ('e', 'close (CCW)', 'Middle'),  # E  → close middle
    'r': ('r', 'close (CCW)', 'Index'),   # R  → close index
    't': ('t', 'close (CCW)', 'Thumb'),   # T  → close thumb

    # ── GROUP COMMANDS ───────────────────────────────────────────
    'o': ('O', 'open  (CW)', 'ALL fingers'),  # O  → open all
    'c': ('C', 'close (CCW)', 'ALL fingers'), # C  → close all
}

print("\nControls (Pinkie → Thumb):")
print("  1-5 = Open individual fingers (CW)")
print("  Q-T = Close individual fingers (CCW)")
print("  O   = Open  ALL")
print("  C   = Close ALL")
print("  Esc = Quit\n")

# ───────── Key handler ─────────
def on_key(event):
    if event.event_type != 'down':       # act once per press
        return

    k = event.name.lower()

    if k == 'esc':
        print("\n[INFO] Esc pressed → exiting …")
        keyboard.unhook_all()
        esp.close()
        sys.exit(0)

    if k in key_to_command:
        cmd_byte, action_text, finger_name = key_to_command[k]
        esp.write(cmd_byte.encode())     # send raw byte to ESP32
        print(f"📤 {action_text.capitalize()} {finger_name} → Sent '{cmd_byte}'")

# ───────── Start listening ─────────
keyboard.hook(on_key)
print("[INFO] Ready. Press keys …")

# ───────── Keep script alive ─────────
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    esp.close()
    print("\n[INFO] Serial port closed.")
