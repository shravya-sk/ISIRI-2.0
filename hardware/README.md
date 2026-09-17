# 🔌 ISIRI 2.0 — Hardware & GPIO Integration Guide

This directory contains the standalone **Raspberry Pi Servo Lock Service** that enables ISIRI 2.0 to lock/unlock a real-world door latch via spoken Tulu commands.

> **Note:** this replaces the earlier relay-based lights/fan design. The mechanism that was actually built is a 3D-printed **rack-and-pinion latch** driven by a single SG90 micro servo — not a relay board.

---

## 1. Hardware Architecture

```text
[Spoken Tulu Voice]
        │
        ▼
[ISIRI 2.0 Backend]
        │ (HTTP REST: POST http://<RPi_IP>:5000/device/lock/{locked|unlocked})
        ▼
[Raspberry Pi Servo Service (`rpi_gpio_service.py`)]
        │ (PWM signal, 0°–180° sweep)
        ▼
[SG90 Micro Servo]
        │ (pinion gear on servo horn)
        ▼
[3D-Printed Rack-and-Pinion Latch]
   └── Pinion rotates 0°↔180° → drives toothed rack bar in/out → 🔒 bolt extends/retracts
```

The servo's horn carries a small pinion gear that meshes with a toothed rack (the straight bar in the print). Rotating the servo through its full sweep drives the rack linearly — that linear motion is what extends or retracts the lock bolt. Because the throw is done by the rack rather than a direct arm, the servo needs its **full 0°–180° range**, not just a small flip.

---

## 2. GPIO Pinout & Wiring

| Component | BCM GPIO Pin | Physical Board Pin | Notes |
| :--- | :--- | :--- | :--- |
| **Lock Servo (signal)** | `GPIO 18` | Pin 12 | Hardware PWM-capable pin, ideal for servo control |
| **Servo VCC** | `5V` | Pin 2 or 4 | SG90 draws power from the 5V rail |
| **Servo GND** | `GND` | Pin 6, 9, 14, etc. | Common ground with the Pi |

Servo wire colors are typically: **orange/yellow** = signal → GPIO 18, **red** = VCC → 5V, **brown/black** = GND → GND.

---

## 3. Calibration

`LOCK_ANGLE` and `UNLOCK_ANGLE` in `rpi_gpio_service.py` are set to `180` and `0` respectively, but the actual "locked" direction depends on which way the pinion meshes with the rack on your specific print. After mounting:

1. Run the service and hit `/device/lock/locked`, then `/device/lock/unlocked`.
2. Watch which direction the rack moves.
3. If it's backwards, swap the two angle values in the script — no other code changes needed.

---

## 4. How to Run on Raspberry Pi

### Step 1: Copy `hardware/rpi_gpio_service.py` to Raspberry Pi
```bash
scp hardware/rpi_gpio_service.py pi@<raspberry_pi_ip>:~/
```

### Step 2: Start the Daemon on Raspberry Pi
```bash
python3 rpi_gpio_service.py --port 5000
```
*Output: `ISIRI 2.0 Lock Service listening on port 5000...`*

### Step 3: Connect ISIRI 2.0 Backend
In your ISIRI 2.0 environment or `.env` file, configure the Raspberry Pi's local network IP:
```bash
export RPI_HOST="http://<raspberry_pi_ip>:5000"
export HARDWARE_SIMULATION="false"
```

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/status` | Returns current lock state (`locked`/`unlocked`) and whether the physical servo or simulation mode is active |
| `POST` | `/device/lock/{state}` | `state` = `locked` or `unlocked` — drives the servo to the corresponding angle |

---

## 6. Supported Voice Commands in Tulu & English

| Voice Command (Tulu) | Voice Command (English) | Action Executed |
| :--- | :--- | :--- |
| `Bagilu lock malpule` | *"Lock the door"* | POST `/device/lock/locked` → servo drives rack to lock position |
| `Bagilu unlock malpule` | *"Unlock the door"* | POST `/device/lock/unlocked` → servo drives rack to unlock position |

> Tulu phrasing above is a placeholder based on the original doc's naming pattern — swap in your team's actual wording for "lock"/"unlock" if it differs.