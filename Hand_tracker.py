import cv2
import mediapipe as mp
import serial
import time
import math

# ───────── Serial (ESP32) ─────────
ESP_PORT = 'COM4'          # ← change if needed
BAUD     = 115_200

try:
    esp = serial.Serial(ESP_PORT, BAUD, timeout=1)
    time.sleep(2)
    print(f"[INFO] Serial open on {ESP_PORT} @ {BAUD} baud")
except serial.SerialException as e:
    raise SystemExit(f"[ERROR] Could not open {ESP_PORT}: {e}")

# ─────────- Timing that matches the ESP32 sketch ─────────
FINGER_TIMES = [1.5, 1.2, 1.5, 1.5, 1.2]   # Pinkie→Thumb (seconds)
INTER_GAP    = 0.05                        # gap between fingers (seconds)
SAFETY_PAD   = 0.3                         # extra safety

TOTAL_SEQ_TIME = sum(FINGER_TIMES) + (len(FINGER_TIMES) - 1) * INTER_GAP
COOLDOWN       = TOTAL_SEQ_TIME + SAFETY_PAD          # ≈ 6.5 s
COOLDOWN       = round(COOLDOWN, 2)                   # nice number

# ───────── MediaPipe setup ─────────
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands()
mp_draw  = mp.solutions.drawing_utils

# ───────── Webcam setup ─────────
cap = cv2.VideoCapture(0)

# ───────── Gesture state ─────────
prev_state       = None      # "open" or "closed"
last_action_time = 0.0

def is_hand_closed(lm):
    """Return True if all fingertips lie below their PIP joints."""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    return all(lm[t].y > lm[p].y for t, p in zip(tips, pips))

print(f"[INFO] Cool-down between state changes set to {COOLDOWN:.2f} s")

# ───────── Main loop ─────────
while True:
    ok, frame = cap.read()
    if not ok:
        continue

    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res   = hands.process(rgb)
    now   = time.time()

    if res.multi_hand_landmarks:
        for handLms in res.multi_hand_landmarks:
            lm = handLms.landmark
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            if is_hand_closed(lm):
                if prev_state != 'closed' and (now - last_action_time) > COOLDOWN:
                    esp.write(b'C')                     # Close all (sequential)
                    print("✊ Gesture: Hand CLOSED  → Sent 'C'")
                    last_action_time = time.time()
                    prev_state = 'closed'
            else:
                if prev_state != 'open' and (now - last_action_time) > COOLDOWN:
                    esp.write(b'O')                     # Release all (sequential)
                    print("🖐️ Gesture: Hand OPEN    → Sent 'O'")
                    last_action_time = time.time()
                    prev_state = 'open'

    # Live countdown
    remaining = COOLDOWN - (time.time() - last_action_time)
    if remaining > 0:
        print(f"⌛ Next gesture in {remaining:4.1f} s", end='\r')

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ───────── Cleanup ─────────
cap.release()
cv2.destroyAllWindows()
esp.close()
print("\n[INFO] Closed camera and serial port.")
