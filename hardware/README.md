# 🔌 ISIRI 2.0 — Hardware & GPIO Integration Guide

This directory contains the standalone **Raspberry Pi GPIO Hardware Service** that enables ISIRI 2.0 to control real-world appliances (Lights, Fans, Relays, LEDs) via spoken Tulu commands.

---

## 1. Hardware Architecture

```text
[Spoken Tulu Voice]
        │
        ▼
[ISIRI 2.0 Backend]
        │ (HTTP REST: POST http://<RPi_IP>:5000/device/light/on)
        ▼
[Raspberry Pi GPIO Service (`rpi_gpio_service.py`)]
        │ (GPIO Signal HIGH/LOW)
        ▼
[5V 4-Channel Relay Module / Breadboard LEDs]
   ├── Relay 1 (GPIO 17) ──> 💡 Room Light
   ├── Relay 2 (GPIO 27) ──> 🌀 Ceiling Fan
   ├── Relay 3 (GPIO 22) ──> ♨️ Geyser / AC
   └── Relay 4 (GPIO 23) ──> 🔌 Extra Socket
```

---

## 2. GPIO Pinout & Circuit Wiring

| Appliance / Device | BCM GPIO Pin | Physical Board Pin | Component |
| :--- | :--- | :--- | :--- |
| **Light** | `GPIO 17` | Pin 11 | IN1 on Relay (or LED + 220Ω resistor) |
| **Fan** | `GPIO 27` | Pin 13 | IN2 on Relay (or LED + 220Ω resistor) |
| **Geyser / AC** | `GPIO 22` | Pin 15 | IN3 on Relay |
| **Socket / Aux** | `GPIO 23` | Pin 16 | IN4 on Relay |
| **Relay VCC** | `5V` | Pin 2 or 4 | VCC on Relay |
| **Ground (GND)** | `GND` | Pin 6 or 9 | GND on Relay / Breadboard |

---

## 3. How to Run on Raspberry Pi

### Step 1: Copy `hardware/rpi_gpio_service.py` to Raspberry Pi
```bash
scp hardware/rpi_gpio_service.py pi@<raspberry_pi_ip>:~/
```

### Step 2: Start the Daemon on Raspberry Pi
```bash
python3 rpi_gpio_service.py --port 5000
```
*Output: `🚀 ISIRI 2.0 GPIO Service listening on port 5000...`*

### Step 3: Connect ISIRI 2.0 Backend
In your ISIRI 2.0 environment or `.env` file, configure the Raspberry Pi's local network IP:
```bash
export RPI_HOST="http://<raspberry_pi_ip>:5000"
export HARDWARE_SIMULATION="false"
```

---

## 4. Supported Voice Commands in Tulu & English

| Voice Command (Tulu) | Voice Command (English) | Action Executed |
| :--- | :--- | :--- |
| `Light on malpule` | *"Turn on the light"* | Sets GPIO 17 HIGH $\rightarrow$ Turns Light ON |
| `Light off malpule` | *"Turn off the light"* | Sets GPIO 17 LOW $\rightarrow$ Turns Light OFF |
| `Fan on malpule` | *"Turn on the fan"* | Sets GPIO 27 HIGH $\rightarrow$ Turns Fan ON |
| `Fan off malpule` | *"Turn off the fan"* | Sets GPIO 27 LOW $\rightarrow$ Turns Fan OFF |
| `Kone da light on malpule` | *"Turn on the bedroom light"* | Turns ON bedroom light with Tulu reply |
