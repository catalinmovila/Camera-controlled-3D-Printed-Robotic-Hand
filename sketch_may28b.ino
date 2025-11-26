#include <ESP32Servo.h>

/* ----------- USER CONFIG ------------- */
const int NUM_SERVOS = 5;

// Order: [Pinkie, Ring, Middle, Index, Thumb]
const int servoPins[NUM_SERVOS]   = {18, 19, 21, 22, 23};   // GPIOs

// Motion directions for CONTINUOUS-rotation servos
const int CLOCKWISE_SPEED         = 10;     // → CLOSE
const int COUNTERCLOCKWISE_SPEED  = 170;    // → RELEASE
const int STOP                    = 90;     // neutral

// Per-finger runtime (ms)
const int fingerTime[NUM_SERVOS]  = {1500, 1200, 1500, 1500, 1200};

// Extra wait between fingers for O / C group commands (ms)
const int INTER_FINGER_PAUSE_MS   = 100;
/* ------------------------------------- */

Servo servos[NUM_SERVOS];

enum FingerState { RELEASED, CLOSED };
FingerState state[NUM_SERVOS] = {
  RELEASED, RELEASED, RELEASED, RELEASED, RELEASED
};

/* spin servo only if state needs to change */
void spinIfNeeded(int idx, bool dirCW)
{
  if (idx < 0 || idx >= NUM_SERVOS) return;

  FingerState desired = dirCW ? CLOSED : RELEASED;
  if (state[idx] == desired) return;                 // already there

  servos[idx].write(dirCW ? CLOCKWISE_SPEED : COUNTERCLOCKWISE_SPEED);
  delay(fingerTime[idx]);                            // run time
  servos[idx].write(STOP);

  state[idx] = desired;                              // save new state
}

void setup()
{
  Serial.begin(115200);

  for (int i = 0; i < NUM_SERVOS; ++i)
  {
    servos[i].attach(servoPins[i], 500, 2400);
    servos[i].write(STOP);
  }

  Serial.println(F("\nReady! Controls (Pinkie → Thumb):"));
  Serial.println(F("  1-5 = CLOSE   individual finger (CW)"));
  Serial.println(F("  Q-T = RELEASE individual finger (CCW)"));
  Serial.println(F("  O   = Sequential RELEASE all"));
  Serial.println(F("  C   = Sequential CLOSE   all"));
}

void loop()
{
  if (!Serial.available()) return;
  char c = Serial.read();

  /* -------- Individual finger commands -------- */
  switch (c)
  {
    case '1': spinIfNeeded(0, true);  break;  // Pinkie  → close
    case '2': spinIfNeeded(1, true);  break;  // Ring    → close
    case '3': spinIfNeeded(2, true);  break;  // Middle  → close
    case '4': spinIfNeeded(3, true);  break;  // Index   → close
    case '5': spinIfNeeded(4, true);  break;  // Thumb   → close

    case 'q': case 'Q': spinIfNeeded(0, false); break;  // Pinkie  → release
    case 'w': case 'W': spinIfNeeded(1, false); break;  // Ring    → release
    case 'e': case 'E': spinIfNeeded(2, false); break;  // Middle  → release
    case 'r': case 'R': spinIfNeeded(3, false); break;  // Index   → release
    case 't': case 'T': spinIfNeeded(4, false); break;  // Thumb   → release

    /* -------- Group RELEASE: O/o -------- */
    case 'O': case 'o':
      Serial.println(F("↗️  Releasing all fingers sequentially…"));
      for (int i = 0; i < NUM_SERVOS; ++i) {
        spinIfNeeded(i, false);                       // CCW
        delay(INTER_FINGER_PAUSE_MS);                 // safety gap
      }
      Serial.println(F("🛑 All fingers released."));
      break;

    /* -------- Group CLOSE: C/c -------- */
    case 'C': case 'c':
      Serial.println(F("↘️  Closing all fingers sequentially…"));
      for (int i = 0; i < NUM_SERVOS; ++i) {
        spinIfNeeded(i, true);                        // CW
        delay(INTER_FINGER_PAUSE_MS);                 // safety gap
      }
      Serial.println(F("🛑 All fingers closed."));
      break;
  }
}
